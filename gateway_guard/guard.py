"""Fail-closed request guard primitives for a future AIX transport gateway."""

from __future__ import annotations

from dataclasses import dataclass
import math
import threading
import time
from typing import Callable


@dataclass(frozen=True)
class GatewayConfig:
    max_body_bytes: int = 1_048_576
    max_clock_skew_seconds: float = 300.0
    replay_ttl_seconds: float = 600.0


@dataclass(frozen=True)
class GuardDecision:
    allowed: bool
    code: str


Authorizer = Callable[[str, str, str], bool]


class GatewayGuard:
    """A single-process prototype guard; not a production network gateway."""

    def __init__(
        self,
        config: GatewayConfig | None = None,
        *,
        authorize: Authorizer | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.config = config or GatewayConfig()
        if self.config.max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive")
        if self.config.max_clock_skew_seconds < 0:
            raise ValueError("max_clock_skew_seconds cannot be negative")
        if self.config.replay_ttl_seconds <= 0:
            raise ValueError("replay_ttl_seconds must be positive")
        self.authorize = authorize
        self.clock = clock
        self._seen_nonces: dict[str, float] = {}
        self._lock = threading.Lock()

    def check(
        self,
        *,
        principal_id: str,
        action: str,
        resource: str,
        body: bytes,
        issued_at: float,
        nonce: str,
    ) -> GuardDecision:
        """Return a stable allow/deny decision; never fail open."""
        if not all(isinstance(v, str) and v.strip() for v in (principal_id, action, resource, nonce)):
            return GuardDecision(False, "invalid_request_context")
        if not isinstance(body, bytes):
            return GuardDecision(False, "invalid_body_type")
        if len(body) > self.config.max_body_bytes:
            return GuardDecision(False, "payload_too_large")
        if not isinstance(issued_at, (int, float)) or not math.isfinite(issued_at):
            return GuardDecision(False, "invalid_timestamp")

        now = self.clock()
        if abs(now - float(issued_at)) > self.config.max_clock_skew_seconds:
            return GuardDecision(False, "stale_request")
        if self.authorize is None:
            return GuardDecision(False, "authorizer_unavailable")

        with self._lock:
            expired = [key for key, expiry in self._seen_nonces.items() if expiry <= now]
            for key in expired:
                del self._seen_nonces[key]
            if nonce in self._seen_nonces:
                return GuardDecision(False, "replay_detected")
            self._seen_nonces[nonce] = now + self.config.replay_ttl_seconds

        try:
            permitted = self.authorize(principal_id, action, resource)
        except Exception:
            with self._lock:
                self._seen_nonces.pop(nonce, None)
            return GuardDecision(False, "authorization_error")

        if not permitted:
            with self._lock:
                self._seen_nonces.pop(nonce, None)
            return GuardDecision(False, "unauthorized")

        return GuardDecision(True, "allowed")
