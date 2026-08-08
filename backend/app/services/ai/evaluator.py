import json
import httpx
from typing import Tuple
from app.schemas.schemas import DiscoveredTopicItem
from app.models.persona import Persona
from app.core.config import settings

async def evaluate_topic_quality(
    topic: DiscoveredTopicItem,
    persona: Persona
) -> Tuple[float, bool, str]:
    """
    Evaluates a discovered topic against persona standards.
    Returns: (quality_score: float, is_approved: bool, rejection_or_approval_reason: str)
    """
    # 1. Try Gemini API evaluation if key is available
    if settings.GEMINI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                prompt = f"""
                You are an elite AI technical content reviewer evaluating a potential topic for an executive AI engineering persona.

                Persona Core Topics: {persona.core_topics}
                Target Audience: {persona.target_audience}
                Min Quality Score Threshold: {persona.min_quality_score}/10.0

                Candidate Topic Title: {topic.title}
                Summary: {topic.summary}
                Category: {topic.category}

                Evaluate this topic on:
                1. Technical Depth & Substance (0-10)
                2. Relevancy to AI/Engineering (0-10)
                3. Novelty & Actionability (0-10)

                Provide output strictly in JSON format:
                {{
                   "score": 8.5,
                   "approved": true,
                   "reason": "Clear explanation of evaluation decision and score rationale."
                }}
                """
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json"}
                }
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    parsed = json.loads(text)
                    score = float(parsed.get("score", 7.5))
                    approved = score >= persona.min_quality_score
                    reason = parsed.get("reason", "Evaluated via Gemini AI model.")
                    return score, approved, reason
        except Exception:
            pass # Fall back to algorithmic evaluation rules below

    # 2. Heuristic evaluation rules engine (deterministic fallback)
    title_lower = topic.title.lower()
    summary_lower = topic.summary.lower()

    # Automatic low-quality / clickbait flags
    clickbait_keywords = ["top 10", "will replace", "next month", "secret trick", "shocking", "easy money", "unbelievable"]
    if any(kw in title_lower for kw in clickbait_keywords):
        return 4.2, False, f"Rejected: Contains clickbait title pattern '{[kw for kw in clickbait_keywords if kw in title_lower][0]}'. Lacks technical depth and engineering rigor."

    # Technical depth indicators
    high_tech_keywords = ["model", "rag", "graphrag", "moe", "gpu", "architecture", "latency", "benchmark", "open-source", "protocol", "scaling", "cluster", "transformers", "agentic"]
    tech_count = sum(1 for kw in high_tech_keywords if kw in title_lower or kw in summary_lower)

    if tech_count >= 3:
        score = 9.1
        reason = "Approved: High technical depth, strong architectural focus, highly relevant to AI engineers and system architects."
    elif tech_count >= 1:
        score = 7.8
        reason = "Approved: Good technical relevance and industry timeliness."
    else:
        score = 5.5
        reason = f"Rejected: Quality score 5.5 is below persona threshold {persona.min_quality_score}. Topic lacks substantial technical depth, architecture insights, or empirical benchmarks."

    is_approved = score >= persona.min_quality_score
    return score, is_approved, reason
