"""Shared quota throttling guard for AI providers.

Interactive chat calls take priority. When any provider reports a quota /
rate-limit (429) error, this guard opens a short cooldown window during
which the autonomous background scheduler skips its AI work (via
``quota_blocked()``) so it stops competing with the user's chat for the
remaining free-tier quota.

The guard is intentionally process-local and simple: it never persists, and
a cold cooldown is benign — the scheduler just runs once more.
"""

import logging
import time

logger = logging.getLogger("AutoPersona-Quota")

COOLDOWN_SECONDS = 75.0

_cooldown_until = 0.0


def report_quota(seconds: float = COOLDOWN_SECONDS) -> None:
    """Remember that a provider reported quota/rate limit for `seconds`."""
    global _cooldown_until
    _cooldown_until = time.monotonic() + max(seconds, 5.0)
    logger.info("Quota guard armed for %.0fs", seconds)


def quota_blocked() -> bool:
    """True while a recent 429 says background AI should stand down."""
    return time.monotonic() < _cooldown_until


def quota_remaining() -> float:
    """Seconds left in the current cooldown (0.0 if none)."""
    return max(0.0, _cooldown_until - time.monotonic())