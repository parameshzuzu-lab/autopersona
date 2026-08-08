import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.core.config import settings
from app.services.ai.chat_service import (
    _safe_eval_math,
    _extract_math_expr,
    _detect_tamil,
    _validate_model_text,
    _build_conversation_messages,
    _fallback_reply,
    _classify_provider_error,
    _build_context_text,
)
from app.services.ai.azure_ai import (
    azure_configured,
    azure_chat_url,
    _post_with_retry,
    classify_provider_error as azure_classify,
)
from app.services.ai import quota_guard
from app.services.ai.quota_guard import quota_blocked, report_quota, quota_remaining
from app.services.ai.knowledge_base import lookup as kb_lookup

FAILURES = []

def check(name, got, expected):
    ok = got == expected
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got={got!r} expected={expected!r}")
    if not ok:
        FAILURES.append(name)

def test_math():
    check("math 25*16", _safe_eval_math("25 * 16"), 400)
    check("math (2+3)*4", _safe_eval_math("(2 + 3) * 4"), 20)
    check("math 100/4", _safe_eval_math("100 / 4"), 25.0)
    check("extract wrapped", _extract_math_expr("Calculate 25 * 16"), "25 * 16")
    check("extract paren", _extract_math_expr("what is (2 + 3) * 4?"), "(2 + 3) * 4")
    check("no math in prose", _extract_math_expr("what is Java?"), None)

def test_tamil():
    check("detect tamil script", _detect_tamil("Java inheritance na enna"), True)
    check("detect tamil word", _detect_tamil("Tamil la sollu"), True)
    check("detect vanakkam", _detect_tamil("Vanakkam!"), True)
    check("no tamil", _detect_tamil("What is inheritance in Java?"), False)

def test_validation():
    check("empty", _validate_model_text("   "), None)
    check("plain", _validate_model_text("hello world"), "hello world")
    check("json wrapper", _validate_model_text('{"reply":"inner text"}'), "inner text")
    check("trailing space", _validate_model_text("  ok  "), "ok")

def test_context():
    msgs = _build_conversation_messages(
        "What are its advantages?",
        [{"role": "user", "content": "What is Java?"}, {"role": "assistant", "content": "Java is a language."}],
        "SYSTEM",
    )
    roles = [m["role"] for m in msgs]
    check("system first", roles[0], "system")
    check("history present", roles[1], "user")
    check("assistant present", roles[2], "assistant")
    check("latest last", roles[-1], "user")

def test_fallback_no_fabrication():
    reply = _fallback_reply("How many users does ChatGPT have right now?", {})["reply"]
    check("no fabrication for unknown", "reliable answer" in reply, True)

def test_knowledge_base():
    check("kb java inheritance", "extends" in kb_lookup("Explain inheritance in Java"), True)
    check("kb fibonacci", "Fibonacci" in kb_lookup("Write a Java program to print fibonacci numbers"), True)
    check("kb oop", "Encapsulation" in kb_lookup("What is object-oriented programming?"), True)
    check("kb nullpointer", "null" in kb_lookup("Why do I get NullPointerException?").lower(), True)
    check("kb python vs java", "Python" in kb_lookup("What is the difference between python vs java"), True)
    check("kb tamil inheritance", "inheritance" in kb_lookup("Java inheritance pathi Tamil la sollu").lower(), True)
    check("kb greeting no match", kb_lookup("hello there!"), None)
    check("kb unknown no match", kb_lookup("What is the price of a Tesla Model 3?"), None)
    check("kb offline fallback", "reliable answer" in _fallback_reply("What is the price of a Tesla Model 3?", {})["reply"], True)

def test_error_classification():
    check("429 -> quota", _classify_provider_error(429, "quota exceeded", "gemini"), "quota")
    check("401 -> invalid_key", _classify_provider_error(401, "unauthorized", "gemini"), "invalid_key")
    check("400 key -> invalid_key", _classify_provider_error(400, "API key not valid", "gemini"), "invalid_key")
    check("404 model -> model_not_found", _classify_provider_error(404, "models/x is not found", "gemini"), "model_not_found")
    check("500 -> api_error", _classify_provider_error(500, "internal error", "gemini"), "api_error")
    check("503 -> api_error", _classify_provider_error(503, "unavailable", "gemini"), "api_error")

def test_context_grounding():
    ctx = {
        "persona": type("P", (), {"name": "TestPersona", "editorial_voice": "Expert tone", "target_audience": "Engineers", "core_topics": "AI"})(),
        "memory": {
            "past_posts_count": 5,
            "discussed_companies": [{"company": "OpenAI", "mentions": 3}],
            "recent_trends": [{"trend": "Agentic AI", "frequency": 2}],
            "editorial_opinions": ["I think X"],
        },
        "posts": [
            {"title": "A post", "content": "content here", "why_relevant_now": "now", "source_urls": ["https://ex.com"]}
        ],
    }
    text = _build_context_text(ctx)
    check("ctx has persona name", "TestPersona" in text, True)
    check("ctx has companies", "OpenAI" in text, True)
    check("ctx has trends", "Agentic AI" in text, True)
    check("ctx has posts", "A post" in text, True)
    check("ctx empty safe", _build_context_text({}), "")

def test_quota_guard():
    report_quota(seconds=5.0)
    check("quota blocked after report", quota_blocked(), True)
    check("quota remaining > 0", quota_remaining() > 0, True)
    check("409 not quota", azure_classify(409, "conflict", "azure"), "api_error")
    check("429 arms blocker", azure_classify(429, "too many requests", "azure"), "quota")
    check("500 not blocker", azure_classify(500, "internal", "azure"), "api_error")

def test_azure_provider():
    check("azure not configured when empty", azure_configured(), False)
    check("azure 401 -> invalid_key", azure_classify(401, "invalid API key",), "invalid_key")
    check("azure 400 key -> invalid_key", azure_classify(400, "Access denied due to invalid subscription key"), "invalid_key")
    check("azure 404 deployment -> model_not_found", azure_classify(404, "The deployment 'gpt-4o' does not exist"), "model_not_found")
    check("azure 429 -> quota", azure_classify(429, "Rate limit is exceeded. Try again in 26 seconds"), "quota")
    check("azure 500 -> api_error", azure_classify(500, "Internal server error"), "api_error")

    old = (settings.AZURE_OPENAI_ENDPOINT, settings.AZURE_OPENAI_DEPLOYMENT, settings.AZURE_OPENAI_API_VERSION)
    try:
        settings.AZURE_OPENAI_ENDPOINT = "https://myres.openai.azure.com/"
        settings.AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"
        settings.AZURE_OPENAI_API_VERSION = "2024-12-01"
        url = azure_chat_url()
        check("azure url has chat/completions", "/openai/deployments/gpt-4o-mini/chat/completions" in url, True)
        check("azure url api-version query", "api-version=2024-12-01" in url, True)
        check("azure url no double slash", "azure.com//openai" not in url, True)
    finally:
        settings.AZURE_OPENAI_ENDPOINT, settings.AZURE_OPENAI_DEPLOYMENT, settings.AZURE_OPENAI_API_VERSION = old

class _FakeResp:
    def __init__(self, status):
        self.status_code = status
        self.headers = {}

class _FakeClient:
    def __init__(self, results, delay=0.0):
        self.results = list(results)
        self.calls = 0
        self.delay = delay
    async def post(self, *_args, **_kwargs):
        self.calls += 1
        if self.delay:
            await asyncio.sleep(self.delay)
        return self.results.pop(0) if self.results else _FakeResp(200)

async def test_retry():
    c = _FakeClient([_FakeResp(429), _FakeResp(429), _FakeResp(200)])
    resp = await _post_with_retry(c, "https://x", body={}, attempts=5, base_delay=0.01)
    check("retry: eventually 200", resp.status_code, 200)
    check("retry: 3 calls made", c.calls, 3)

    c2 = _FakeClient([_FakeResp(429), _FakeResp(429), _FakeResp(429), _FakeResp(429), _FakeResp(429)])
    resp2 = await _post_with_retry(c2, "https://x", body={}, attempts=5, base_delay=0.01)
    check("retry: exhausts and returns 429", resp2.status_code, 429)
    check("retry: calls capped at attempts", c2.calls, 5)

async def main():
    test_math()
    test_tamil()
    test_validation()
    test_context()
    test_fallback_no_fabrication()
    test_knowledge_base()
    test_error_classification()
    test_context_grounding()
    test_azure_provider()
    await test_retry()
    print(f"\n{len(FAILURES)} failure(s)" if FAILURES else "\nALL PASSED")

if __name__ == "__main__":
    asyncio.run(main())
