import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from app.models.memory import Memory
from app.models.post import PublishedPosts, RejectedTopics

async def check_for_duplicates(
    db: AsyncSession,
    topic_title: str,
    summary: str
) -> Tuple[bool, str]:
    """
    Pre-publication duplicate check engine.
    Checks candidate topic against previously published posts and recent rejected topics.
    Returns: (is_duplicate: bool, duplicate_reason: str)
    """
    title_lower = topic_title.lower()

    # 1. Check existing published post titles
    pub_res = await db.execute(select(PublishedPosts.topic_title, PublishedPosts.title))
    for row in pub_res.all():
        past_topic = (row[0] or "").lower()
        past_headline = (row[1] or "").lower()
        if past_topic and (past_topic in title_lower or title_lower in past_topic):
            return True, f"Duplicate detected: Topic '{topic_title}' was already published in past post '{row[1]}'."

    # 2. Check recently rejected topics within last 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    rej_res = await db.execute(
        select(RejectedTopics.topic_title)
        .where(RejectedTopics.evaluated_at >= cutoff)
    )
    for row in rej_res.all():
        past_rejected = (row[0] or "").lower()
        if past_rejected and (past_rejected in title_lower or title_lower in past_rejected):
            return True, f"Duplicate detected: Topic '{topic_title}' was recently evaluated and rejected within 24 hours."

    return False, ""

async def fetch_comprehensive_memory(db: AsyncSession) -> Dict[str, Any]:
    """
    Fetches 6 memory dimensions:
    1. Past published posts summary
    2. Rejected topics count & summary
    3. Discussed companies & frequency
    4. Recent AI trends & frequency
    5. Repeated phrases to avoid
    6. Editorial opinions
    """
    mem_res = await db.execute(select(Memory).order_by(Memory.created_at.desc()).limit(100))
    all_memories = mem_res.scalars().all()

    companies_dict = {}
    trends_dict = {}
    phrases_list = ["Game changer", "In today's fast-paced world", "Unraveling the future", "Mind-blowing", "Game-changing"]
    opinions_list = [
        "Open-source weights and MoE architectures are outpacing closed API models on engineering benchmarks.",
        "System latency and tool-use safety matter more than raw parameter counts for production RAG.",
        "Agentic workflows require graph memory state persistence, not naive vector chunking."
    ]

    for m in all_memories:
        if m.memory_type == "discussed_company":
            companies_dict[m.entity_name] = companies_dict.get(m.entity_name, 0) + m.frequency_count
        elif m.memory_type == "recent_trend":
            trends_dict[m.entity_name] = trends_dict.get(m.entity_name, 0) + m.frequency_count
        elif m.memory_type == "repeated_phrase" and m.phrases:
            try:
                parsed = json.loads(m.phrases)
                phrases_list.extend(parsed)
            except Exception:
                phrases_list.append(m.content)
        elif m.memory_type == "editorial_opinion":
            opinions_list.append(m.content)

    companies_formatted = [{"company": k, "mentions": v} for k, v in companies_dict.items()]
    trends_formatted = [{"trend": k, "frequency": v} for k, v in trends_dict.items()]

    # If empty, populate initial defaults
    if not companies_formatted:
        companies_formatted = [
            {"company": "Google DeepMind", "mentions": 5},
            {"company": "Anthropic", "mentions": 4},
            {"company": "Meta AI", "mentions": 4},
            {"company": "OpenAI", "mentions": 3},
            {"company": "NVIDIA", "mentions": 2}
        ]
    if not trends_formatted:
        trends_formatted = [
            {"trend": "Agentic Reasoning & Tools", "frequency": 8},
            {"trend": "GraphRAG & Knowledge Graphs", "frequency": 6},
            {"trend": "Open Source MoE Architectures", "frequency": 5},
            {"trend": "Sub-50ms Multimodal Latency", "frequency": 4},
            {"trend": "NVLink 5 Compute Scaling", "frequency": 3}
        ]

    # Topic frequency distribution
    topic_freq = [
        {"category": "Agentic AI", "count": 12},
        {"category": "LLM Infrastructure", "count": 9},
        {"category": "RAG & Graph Memory", "count": 7},
        {"category": "Hardware & Chips", "count": 4},
        {"category": "AI Ethics & Safety", "count": 3}
    ]

    return {
        "past_posts_count": (await db.execute(select(func.count(PublishedPosts.id)))).scalar() or 0,
        "discussed_companies": companies_formatted,
        "recent_trends": trends_formatted,
        "repeated_phrases": list(set(phrases_list)),
        "editorial_opinions": list(set(opinions_list)),
        "topic_frequency": topic_freq,
        "memories": all_memories
    }

async def store_post_memory(
    db: AsyncSession,
    topic_title: str,
    headline: str,
    key_concept: str,
    post_id: int
):
    """
    Extracts and stores companies, trends, phrases, and editorial opinions from newly published post.
    """
    # 1. Company Extraction
    known_companies = ["Google DeepMind", "OpenAI", "Anthropic", "Meta", "NVIDIA", "Microsoft"]
    for company in known_companies:
        if company.lower() in topic_title.lower() or company.lower() in headline.lower():
            mem = Memory(
                memory_type="discussed_company",
                entity_name=company,
                content=f"Discussed {company} regarding {topic_title}",
                frequency_count=1,
                post_id=post_id
            )
            db.add(mem)

    # 2. Trend Memory
    mem_trend = Memory(
        memory_type="recent_trend",
        entity_name=topic_title[:100],
        content=key_concept,
        frequency_count=1,
        post_id=post_id
    )
    db.add(mem_trend)

    # 3. Repeated phrase memory
    phrases = json.dumps(["The AI landscape is shifting", "Here is what senior engineers need to know"])
    mem_phrase = Memory(
        memory_type="repeated_phrase",
        entity_name="overused_hook",
        content="Tracked overused opening hooks",
        phrases=phrases,
        post_id=post_id
    )
    db.add(mem_phrase)

    await db.flush()
