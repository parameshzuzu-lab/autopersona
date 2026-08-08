import asyncio
import json
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.persona import Persona
from app.models.post import PublishedPosts, RejectedTopics
from app.models.scheduler import SchedulerStatus, ExecutionLog
from app.services.ai.news_fetcher import fetch_latest_ai_topics
from app.services.ai.evaluator import evaluate_topic_quality
from app.services.ai.writer import generate_linkedin_post
from app.services.ai.memory_service import check_for_duplicates, fetch_comprehensive_memory, store_post_memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoPersona-Scheduler")

scheduler = AsyncIOScheduler()

async def run_autonomous_cycle():
    """
    Core Autonomous Cycle executed every 15 minutes:
    1. Fetches latest AI news/topics.
    2. Runs pre-publication duplicate check against memory.
    3. Evaluates quality score against Persona threshold & stores rejected topics.
    4. Passes 6-dimensional Memory context to AI Writer.
    5. Generates LinkedIn-style post (JSON formatted, <= 250 words) with complete metadata.
    6. Stores post in PublishedPosts and extracts entity memory concepts.
    7. Updates SchedulerStatus and logs audit trail.
    """
    logger.info("⚡ Starting autonomous AI discovery & publishing cycle...")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch or initialize active Persona
            res = await db.execute(select(Persona).where(Persona.is_active == True))
            persona = res.scalars().first()
            if not persona:
                persona = Persona(
                    name="AutoPersona AI",
                    editorial_voice="Authoritative, vision-driven AI researcher and tech strategist.",
                    target_audience="AI Engineers, Software Architects, Tech Executives",
                    core_topics="LLMs, Agentic AI, Autonomous Systems, Compute Infrastructure",
                    min_quality_score=settings.MIN_QUALITY_SCORE
                )
                db.add(persona)
                await db.flush()

            # Update status to executing
            st_res = await db.execute(select(SchedulerStatus))
            status_rec = st_res.scalars().first()
            if not status_rec:
                status_rec = SchedulerStatus(status="executing", interval_minutes=settings.SCHEDULER_INTERVAL_MINUTES)
                db.add(status_rec)
            else:
                status_rec.status = "executing"
            await db.commit()

            # Log cycle start
            db.add(ExecutionLog(level="INFO", message="Autonomous cycle initialized", details="Fetching live AI topics..."))
            await db.commit()

            # 2. Fetch latest AI topics
            topics = await fetch_latest_ai_topics()
            if not topics:
                db.add(ExecutionLog(level="WARN", message="No new topics discovered in current cycle", details="Retrying next interval."))
                status_rec.status = "running"
                status_rec.last_run_at = datetime.utcnow()
                status_rec.next_run_at = datetime.utcnow() + timedelta(minutes=settings.SCHEDULER_INTERVAL_MINUTES)
                await db.commit()
                return

            # 3. Retrieve comprehensive memory
            memory_context = await fetch_comprehensive_memory(db)

            # 4. Duplicate Check & Quality Evaluation
            approved_candidates = []
            new_rejected_count = 0

            for topic in topics:
                # Pre-publication duplicate check
                is_dup, dup_reason = await check_for_duplicates(db, topic.title, topic.summary)
                if is_dup:
                    rej = RejectedTopics(
                        topic_title=topic.title,
                        source_url=topic.source_url,
                        rejection_reason=dup_reason,
                        quality_score=4.0,
                        evaluated_at=datetime.utcnow()
                    )
                    db.add(rej)
                    new_rejected_count += 1
                    continue

                # Quality evaluation
                score, is_approved, reason = await evaluate_topic_quality(topic, persona)
                await asyncio.sleep(2.0)
                if is_approved:
                    approved_candidates.append((topic, score, reason))
                else:
                    rej = RejectedTopics(
                        topic_title=topic.title,
                        source_url=topic.source_url,
                        rejection_reason=reason,
                        quality_score=score,
                        evaluated_at=datetime.utcnow()
                    )
                    db.add(rej)
                    new_rejected_count += 1

            await db.commit()

            if not approved_candidates:
                msg = f"All {len(topics)} discovered topics were rejected due to duplicate memory detection or quality threshold."
                logger.info(f"⚠️ {msg}")
                db.add(ExecutionLog(level="WARN", message="Autonomous cycle completed without publishing", details=msg))
                status_rec.status = "running"
                status_rec.last_run_at = datetime.utcnow()
                status_rec.next_run_at = datetime.utcnow() + timedelta(minutes=settings.SCHEDULER_INTERVAL_MINUTES)
                status_rec.total_runs += 1
                status_rec.total_rejected += new_rejected_count
                await db.commit()
                return

            # 5. Pick the top-scoring candidate topic
            approved_candidates.sort(key=lambda x: x[1], reverse=True)
            best_topic, best_score, best_reason = approved_candidates[0]

            logger.info(f"✨ Selected Best Topic (Score {best_score}): {best_topic.title}")

            # 6. Generate LinkedIn-style post JSON payload (max 250 words)
            post_payload = await generate_linkedin_post(best_topic, persona, memory_context)

            # 7. Store post in PublishedPosts
            post = PublishedPosts(
                title=post_payload["title"],
                content=post_payload["body"],
                topic_title=best_topic.title,
                why_selected=post_payload.get("why_selected", best_reason),
                why_relevant_now=post_payload.get("why_relevant_now", "High industry timeliness."),
                source_urls=json.dumps(post_payload.get("source_urls", [best_topic.source_url])),
                hashtags=json.dumps(post_payload.get("hashtags", ["#AI", "#Tech"])),
                editorial_score=float(post_payload.get("editorial_score", best_score)),
                confidence_score=float(post_payload.get("confidence_score", 0.94)),
                published_at=datetime.utcnow(),
                persona_id=persona.id
            )
            db.add(post)
            await db.flush()

            # Store memory concepts
            await store_post_memory(
                db=db,
                topic_title=best_topic.title,
                headline=post_payload["title"],
                key_concept=post_payload.get("why_selected", best_topic.title),
                post_id=post.id
            )

            # 8. Log success & update status record
            status_rec.status = "running"
            status_rec.last_run_at = datetime.utcnow()
            status_rec.next_run_at = datetime.utcnow() + timedelta(minutes=settings.SCHEDULER_INTERVAL_MINUTES)
            status_rec.total_runs += 1
            status_rec.total_published += 1
            status_rec.total_rejected += new_rejected_count

            db.add(ExecutionLog(
                level="SUCCESS",
                message=f"Published LinkedIn post: '{post_payload['title']}'",
                details=f"Topic: {best_topic.title} | Score: {best_score}/10 | Rejections this run: {new_rejected_count}"
            ))
            await db.commit()

            logger.info(f"✅ Successfully published post #{post.id}: {post_payload['title']}")

        except Exception as e:
            logger.error(f"❌ Error in autonomous cycle: {str(e)}", exc_info=True)
            db.add(ExecutionLog(level="ERROR", message="Autonomous cycle encountered error", details=str(e)))
            if status_rec:
                status_rec.status = "running"
                status_rec.last_error = str(e)
            await db.commit()

def start_autonomous_scheduler():
    """
    Initializes and starts APScheduler on startup. Runs every 15 minutes automatically.
    """
    if not scheduler.running:
        scheduler.add_job(
            run_autonomous_cycle,
            'interval',
            minutes=settings.SCHEDULER_INTERVAL_MINUTES,
            id='autopersona_15min_publisher',
            replace_existing=True,
            next_run_time=datetime.utcnow()
        )
        scheduler.start()
        logger.info(f"🚀 Autonomous APScheduler started! Interval: Every {settings.SCHEDULER_INTERVAL_MINUTES} minutes.")
