"""
Microsoft Azure OpenAI / Azure AI Foundry provider.

Official API (verified, current):
    POST https://<resource>.openai.azure.com/openai/deployments/<deployment>/chat/completions?api-version=<version>
    Headers: Content-Type: application/json, api-key: <key>
    Body:    { "messages": [...], "temperature": ..., "max_tokens": ... }
    Reply:   choices[0].message.content

* The key travels in the `api-key` HEADER, never in the URL.
* Never log the key, the endpoint (may embed credentials), or user content.
* The `messages` array already uses the system/user/assistant roles that both
  this provider and the rest of the chat engine use.
"""

import asyncio
import json
import logging
from typing import List, Optional

import httpx

from app.core.config import settings
from app.services.ai import quota_guard

logger = logging.getLogger("AutoPersona-Azure")


class AzureProviderError(Exception):
    """Azure OpenAI call failed. `kind` is a safe, user-facing error category."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind
        self.message = message


def classify_provider_error(status: int, detail: str, provider: str = "") -> str:
    """Map Azure/HTTP status + message to a safe error kind. `provider` is optional and unused.

    A 429 arms the shared quota guard so the background scheduler stops
    competing with interactive chat for remaining free-tier quota.
    """
    low = (detail or "").lower()
    if status == 429:
        quota_guard.report_quota()
    if status in (400, 403, 404):
        if any(
            k in low
            for k in (
                "api key",
                "subscription key",
                "invalid key",
                "access denied",
                "denied",
                "unauthorized",
                "permission",
                "invalid argument",
            )
        ):
            return "invalid_key"
        if status == 404 or "not found" in low or "deployment" in low or "no longer available" in low or "not supported" in low:
            return "model_not_found"
        return "invalid_request"
    if status == 401:
        return "invalid_key"
    if status == 429:
        return "quota"
    if status >= 500:
        return "api_error"
    return "api_error"


def azure_configured() -> bool:
    return bool(
        settings.AZURE_OPENAI_API_KEY
        and settings.AZURE_OPENAI_ENDPOINT
        and settings.AZURE_OPENAI_DEPLOYMENT
    )


def azure_chat_url() -> str:
    endpoint = settings.AZURE_OPENAI_ENDPOINT.rstrip("/")
    return (
        f"{endpoint}/openai/deployments/{settings.AZURE_OPENAI_DEPLOYMENT}"
        f"/chat/completions?api-version={settings.AZURE_OPENAI_API_VERSION}"
    )


async def _post_with_retry(
    client: httpx.AsyncClient,
    url: str,
    *,
    body: Optional[dict] = None,
    headers: Optional[dict] = None,
    attempts: int = 5,
    base_delay: float = 1.5,
) -> httpx.Response:
    """POST with exponential backoff on 429, 5xx, timeouts, and network errors.

    Retries are capped (~22s total) so a chat request never hangs. The final
    non-2xx response (e.g. a persistent 429) is returned so callers can classify
    it. Never logs the URL or headers (secrets may be present).
    """
    last_exc: Optional[Exception] = None
    for attempt in range(attempts):
        try:
            resp = await client.post(url, json=body, headers=headers)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_exc = exc
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(min(base_delay * (2 ** attempt), 20.0))
            continue

        if resp.status_code == 429 and attempt < attempts - 1:
            delay = base_delay * (2 ** attempt)
            retry_after = resp.headers.get("retry-after")
            if retry_after:
                try:
                    delay = min(float(retry_after) + 0.5, 20.0)
                except ValueError:
                    pass
            await asyncio.sleep(delay)
            continue

        if resp.status_code >= 500 and attempt < attempts - 1:
            await asyncio.sleep(min(base_delay * (2 ** attempt), 20.0))
            continue

        return resp

    raise last_exc or httpx.NetworkError("POST failed after retries")


async def _post(payload: dict, timeout: float) -> httpx.Response:
    headers = {
        "Content-Type": "application/json",
        "api-key": settings.AZURE_OPENAI_API_KEY,
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            return await _post_with_retry(client, azure_chat_url(), body=payload, headers=headers)
    except httpx.TimeoutException as exc:
        raise AzureProviderError("timeout", "Azure OpenAI request timed out.") from exc
    except httpx.NetworkError as exc:
        raise AzureProviderError("network", "Could not reach the Azure OpenAI endpoint.") from exc
    except Exception as exc:
        raise AzureProviderError("api_error", "Unexpected error calling Azure OpenAI.") from exc


def _raise_on_error(resp: httpx.Response) -> None:
    if resp.status_code < 400:
        return
    detail = ""
    try:
        body = resp.json()
        if isinstance(body, dict):
            err = body.get("error")
            detail = err.get("message", "") if isinstance(err, dict) else str(body)
    except Exception:
        pass
    kind = classify_provider_error(resp.status_code, detail)
    # Log status + provider message only. Never the URL or the api-key header.
    logger.warning(
        "Azure OpenAI error: status=%s kind=%s detail=%s",
        resp.status_code,
        kind,
        (detail or "")[:300],
    )
    raise AzureProviderError(kind, detail or f"Azure OpenAI HTTP {resp.status_code}")


def _extract_content(data: dict) -> str:
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AzureProviderError("api_error", "Unexpected Azure OpenAI response shape.") from exc


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return cleaned


async def azure_chat(messages: List[dict], timeout: Optional[float] = None) -> str:
    """Chat completions call. Returns the assistant text. Raises AzureProviderError."""
    payload = {
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": settings.CHAT_MAX_OUTPUT_TOKENS,
    }
    resp = await _post(payload, timeout or settings.CHAT_TIMEOUT_SECONDS)
    _raise_on_error(resp)
    return _extract_content(resp.json())


async def azure_generate_json(prompt: str, timeout: Optional[float] = None) -> dict:
    """Single-prompt JSON generation used by the autonomous publisher."""
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON-only assistant. Respond ONLY with valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": settings.CHAT_MAX_OUTPUT_TOKENS,
        "response_format": {"type": "json_object"},
    }
    resp = await _post(payload, timeout or settings.CHAT_TIMEOUT_SECONDS)
    _raise_on_error(resp)
    text = _strip_code_fence(_extract_content(resp.json()))
    try:
        parsed = json.loads(text)
    except Exception as exc:
        raise AzureProviderError("invalid_request", "Azure returned malformed JSON.") from exc
    if not isinstance(parsed, dict):
        raise AzureProviderError("invalid_request", "Azure returned a non-object JSON value.")
    return parsed
