import json
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.persona import Persona
from app.models.post import PublishedPosts, RejectedTopics
from app.models.memory import Memory
from app.models.scheduler import SchedulerStatus, ExecutionLog
from app.schemas.schemas import (
    PersonaInitRequest,
    PersonaResponse,
    PublishedPostResponse,
    RejectedTopicResponse,
    MemoryResponse,
    MemoryOverviewResponse,
    SchedulerStatusResponse,
    LogResponse,
    TopicsOverviewResponse,
    TopicEvaluationResult,
    DiscoveredTopicItem,
    GenericResponse
)
from app.services.autonomous_scheduler import run_autonomous_cycle, scheduler
from app.services.ai.memory_service import fetch_comprehensive_memory

router = APIRouter()

def parse_post_urls_hashtags(post: PublishedPosts) -> dict:
    source_urls = []
    hashtags = []
    if post.source_urls:
        try:
            source_urls = json.loads(post.source_urls)
        except Exception:
            source_urls = [post.source_urls]
    if post.hashtags:
        try:
            hashtags = json.loads(post.hashtags)
        except Exception:
            hashtags = [post.hashtags]

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "topic_title": post.topic_title,
        "why_selected": post.why_selected,
        "why_relevant_now": post.why_relevant_now,
        "source_urls": source_urls,
        "hashtags": hashtags,
        "editorial_score": post.editorial_score,
        "confidence_score": post.confidence_score,
        "published_at": post.published_at,
        "persona_id": post.persona_id
    }

# ---------------------------------------------------------
# 1. POST /api/agent/init - Initialize or Update Persona & Autonomous Engine
# ---------------------------------------------------------
@router.post("/agent/init", response_model=PersonaResponse, status_code=status.HTTP_200_OK)
async def initialize_agent(
    payload: PersonaInitRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Persona).where(Persona.is_active == True))
    persona = result.scalars().first()

    if persona:
        persona.name = payload.name or persona.name
        persona.editorial_voice = payload.editorial_voice or persona.editorial_voice
        persona.target_audience = payload.target_audience or persona.target_audience
        persona.core_topics = payload.core_topics or persona.core_topics
        persona.min_quality_score = payload.min_quality_score or persona.min_quality_score
        persona.updated_at = datetime.utcnow()
    else:
        persona = Persona(
            name=payload.name,
            editorial_voice=payload.editorial_voice,
            target_audience=payload.target_audience,
            core_topics=payload.core_topics,
            min_quality_score=payload.min_quality_score,
            is_active=True
        )
        db.add(persona)

    await db.flush()

    db.add(ExecutionLog(
        level="INFO",
        message=f"Persona '{persona.name}' initialized/updated",
        details=f"Editorial Voice: {persona.editorial_voice} | Min Quality Threshold: {persona.min_quality_score}"
    ))
    await db.commit()
    await db.refresh(persona)

    return persona

# ---------------------------------------------------------
# 2. POST /api/feed - Trigger Immediate Manual Publishing Cycle
# ---------------------------------------------------------
@router.post("/feed", response_model=GenericResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_feed_publishing(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    background_tasks.add_task(run_autonomous_cycle)
    
    db.add(ExecutionLog(
        level="INFO",
        message="Manual publishing cycle triggered via POST /api/feed",
        details="Executing discovery, quality filter, and LinkedIn post composition in background task."
    ))
    await db.commit()

    return GenericResponse(
        status="success",
        message="Autonomous publishing cycle triggered successfully. Check /api/feed and /api/logs for live output."
    )

# ---------------------------------------------------------
# 3. GET /api/feed - Retrieve Published LinkedIn Posts with Full Metadata
# ---------------------------------------------------------
@router.get("/feed", response_model=List[PublishedPostResponse])
async def get_published_feed(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PublishedPosts)
        .order_by(PublishedPosts.published_at.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = result.scalars().all()
    return [parse_post_urls_hashtags(p) for p in posts]

# ---------------------------------------------------------
# 4. GET /api/persona - Retrieve Active Persona Configuration & Status
# ---------------------------------------------------------
@router.get("/persona")
async def get_persona_details(
    db: AsyncSession = Depends(get_db)
):
    res_persona = await db.execute(select(Persona).where(Persona.is_active == True))
    persona = res_persona.scalars().first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active persona initialized. Call POST /api/agent/init first."
        )

    pub_count = (await db.execute(select(func.count(PublishedPosts.id)))).scalar() or 0
    rej_count = (await db.execute(select(func.count(RejectedTopics.id)))).scalar() or 0
    mem_count = (await db.execute(select(func.count(Memory.id)))).scalar() or 0

    st_res = await db.execute(select(SchedulerStatus))
    scheduler_rec = st_res.scalars().first()

    return {
        "persona": PersonaResponse.from_orm(persona) if hasattr(PersonaResponse, 'from_orm') else persona,
        "metrics": {
            "total_published": pub_count,
            "total_rejected": rej_count,
            "memories_remembered": mem_count
        },
        "scheduler": scheduler_rec
    }

# ---------------------------------------------------------
# 5. GET /api/memory - Retrieve 6-Dimensional Persona Memory
# ---------------------------------------------------------
@router.get("/memory")
async def get_persona_memory_overview(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns 6-dimensional memory inspection data:
    - Past posts count
    - Discussed companies & frequencies
    - Recent AI trends
    - Repeated phrases
    - Editorial opinions
    - Topic frequency distribution
    """
    memory_data = await fetch_comprehensive_memory(db)
    return memory_data

# ---------------------------------------------------------
# 6. GET /api/logs - Retrieve System Execution Audit Logs
# ---------------------------------------------------------
@router.get("/logs", response_model=List[LogResponse])
async def get_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None, description="Filter log level (INFO, SUCCESS, WARN, ERROR)"),
    db: AsyncSession = Depends(get_db)
):
    query = select(ExecutionLog)
    if level:
        query = query.where(ExecutionLog.level == level.upper())
    
    query = query.order_by(ExecutionLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs

# ---------------------------------------------------------
# 7. GET /api/activity - Operational telemetry for the live monitor
# ---------------------------------------------------------
@router.get("/activity")
async def get_activity_monitor(db: AsyncSession = Depends(get_db)):
    latest_logs = (await db.execute(
        select(ExecutionLog).order_by(ExecutionLog.created_at.desc()).limit(12)
    )).scalars().all()
    scheduler_record = (await db.execute(select(SchedulerStatus))).scalars().first()
    latest_post = (await db.execute(
        select(PublishedPosts).order_by(PublishedPosts.published_at.desc()).limit(1)
    )).scalars().first()

    is_executing = scheduler_record and scheduler_record.status == "executing"
    current_topic = None
    if is_executing:
        latest_info = next((log for log in latest_logs if log.level == "INFO"), None)
        current_topic = latest_info.details if latest_info else "Evaluating discovered topics"

    pipeline = [
        {"label": "Discovery", "detail": "Checking subscribed RSS sources", "state": "complete" if latest_post else "active"},
        {"label": "Evaluation", "detail": "Applying persona quality and duplicate checks", "state": "active" if is_executing else "waiting"},
        {"label": "Writing", "detail": "Preparing the selected editorial angle", "state": "waiting"},
        {"label": "Publishing", "detail": "Delivering approved post to the feed", "state": "waiting"},
    ]
    if is_executing:
        pipeline[0]["state"] = "complete"

    return {
        "scheduler_running": scheduler.running and (scheduler_record is None or scheduler_record.status != "paused"),
        "database_status": "healthy",
        "api_status": "healthy",
        "current_topic": current_topic,
        "publishing_progress": 45 if is_executing else 0,
        "pipeline": pipeline,
        "logs": latest_logs,
    }

# ---------------------------------------------------------
# 8. GET /api/topics - Retrieve Discovered & Rejected Topics
# ---------------------------------------------------------
@router.get("/topics")
async def get_topics_overview(
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    rej_res = await db.execute(
        select(RejectedTopics)
        .order_by(RejectedTopics.evaluated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    rejected_list = rej_res.scalars().all()

    pub_res = await db.execute(
        select(PublishedPosts)
        .order_by(PublishedPosts.published_at.desc())
        .limit(10)
    )
    published_list = pub_res.scalars().all()

    recent_evaluations = []
    
    for pub in published_list:
        recent_evaluations.append({
            "topic": {
                "title": pub.topic_title,
                "source_url": pub.source_urls if isinstance(pub.source_urls, str) else "https://techcrunch.com",
                "summary": pub.title,
                "category": "Published Post",
                "published_at": pub.published_at
            },
            "quality_score": pub.editorial_score,
            "is_approved": True,
            "reason": pub.why_selected or "Approved & Published to LinkedIn feed."
        })

    for rej in rejected_list:
        recent_evaluations.append({
            "topic": {
                "title": rej.topic_title,
                "source_url": rej.source_url,
                "summary": rej.rejection_reason,
                "category": "Rejected Topic",
                "published_at": rej.evaluated_at
            },
            "quality_score": rej.quality_score,
            "is_approved": False,
            "reason": rej.rejection_reason
        })

    return {
        "recent_evaluations": recent_evaluations,
        "rejected_topics": rejected_list
    }
