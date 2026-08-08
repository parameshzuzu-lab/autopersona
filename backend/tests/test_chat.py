import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.services.ai.chat_service import (
    _safe_eval_math,
    _extract_math_expr,
    _detect_tamil,
    _validate_model_text,
    _build_conversation_messages,
    _fallback_reply,
)

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

async def main():
    test_math()
    test_tamil()
    test_validation()
    test_context()
    test_fallback_no_fabrication()
    print(f"\n{len(FAILURES)} failure(s)" if FAILURES else "\nALL PASSED")

if __name__ == "__main__":
    asyncio.run(main())
