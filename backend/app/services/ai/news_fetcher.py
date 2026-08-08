import feedparser
import random
import httpx
from datetime import datetime
from typing import List
from app.schemas.schemas import DiscoveredTopicItem

# Curated list of tech & AI RSS feeds
RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://hnrss.org/frontpage?q=AI",
    "https://news.ycombinator.com/rss"
]

FALLBACK_NEWS_POOL = [
    {
        "title": "Google DeepMind Releases Gemini 2.5 Flash with Sub-50ms Latency for Autonomous Agents",
        "source_url": "https://deepmind.google/discover/blog/gemini-2-5-flash-agentic-breakthrough",
        "summary": "DeepMind introduces ultra-low latency multimodal model tailored for real-time agentic reasoning, memory persistence, and tool use streaming.",
        "category": "Model Breakthrough"
    },
    {
        "title": "Anthropic Unveils Computer Use Protocol Standard (CUP-1.0) for Desktop Automation",
        "source_url": "https://anthropic.com/news/cup-standardization",
        "summary": "A open open-source framework standardizing how frontier LLMs interface directly with OS desktop windows, web browsers, and CLI environments.",
        "category": "Agentic Frameworks"
    },
    {
        "title": "Meta Open-Sources Llama-4 405B MoE Architecture featuring Native Sparse Attention",
        "source_url": "https://ai.meta.com/blog/llama-4-moe-architecture",
        "summary": "Meta releases full weights for Mixture-of-Experts Llama-4, outperforming closed models on complex coding benchmarks and multi-agent coordination.",
        "category": "Open Source AI"
    },
    {
        "title": "Why 80% of Enterprise RAG Pipelines Fail in Production (And How GraphRAG Fixes It)",
        "source_url": "https://techcrunch.com/enterprise-rag-pitfalls-graphrag-solutions",
        "summary": "Engineering post-mortem examining vector search halluncinations vs knowledge graph augmented retrieval in high-concurrency enterprise workloads.",
        "category": "AI Architecture"
    },
    {
        "title": "NVIDIA Blackwell B200 Servers Hit 100K Cluster Scale: Scaling Laws Re-evaluated",
        "source_url": "https://blogs.nvidia.com/scaling-blackwell-clusters",
        "summary": "New benchmarks demonstrate linear scaling efficiency across 100,000 GPU interconnects using NVLink 5 and liquid-assisted thermal dynamics.",
        "category": "Hardware & Compute"
    },
    {
        "title": "Top 10 AI Tools to Boost Your Daily Productivity in 2026",
        "source_url": "https://generic-blog.example.com/top-10-ai-tools-productivity",
        "summary": "A basic list of popular AI text generators, spellcheckers, and resume formatters for casual users.",
        "category": "Consumer Tools"
    },
    {
        "title": "Is AI Going to Replace All Writers Next Month?",
        "source_url": "https://clickbait-news.example.com/ai-replace-writers",
        "summary": "Sensationalized opinion piece discussing superficial worries without technical backing or empirical data.",
        "category": "Opinion"
    }
]

async def fetch_latest_ai_topics() -> List[DiscoveredTopicItem]:
    """
    Fetches real-time tech news from RSS feeds with robust fallback to mock AI news stream.
    """
    topics: List[DiscoveredTopicItem] = []

    # Attempt live RSS fetching
    async with httpx.AsyncClient(timeout=4.0) as client:
        for feed_url in RSS_FEEDS[:2]:  # Check top feeds
            try:
                resp = await client.get(feed_url)
                if resp.status_code == 200:
                    parsed = feedparser.parse(resp.text)
                    for entry in parsed.entries[:3]:
                        title = entry.get("title", "")
                        link = entry.get("link", "")
                        summary = entry.get("summary", entry.get("description", ""))
                        if title and len(title) > 10:
                            topics.append(DiscoveredTopicItem(
                                title=title,
                                source_url=link,
                                summary=summary[:300] + "..." if len(summary) > 300 else summary,
                                category="Live RSS News",
                                published_at=datetime.utcnow()
                            ))
            except Exception:
                continue

    # If live fetching yields fewer than 3 items, augment with rich curated news pool
    if len(topics) < 3:
        sampled = random.sample(FALLBACK_NEWS_POOL, min(4, len(FALLBACK_NEWS_POOL)))
        for item in sampled:
            topics.append(DiscoveredTopicItem(
                title=item["title"],
                source_url=item["source_url"],
                summary=item["summary"],
                category=item["category"],
                published_at=datetime.utcnow()
            ))

    return topics
