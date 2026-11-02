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
    max_replay_entries: int = 10_000
    max_principal_id_chars: int = 256
    max_action_chars: int = 256
    max_resource_chars: int = 1_024
    max_nonce_chars: int = 256


@dataclass(frozen=True)
class GuardDecision:
    allowed: bool
    code: str


Authorizer = Callable[[str, str, str], bool]


class GatewayGuard:
    """A bounded, single-process prototype guard; not a production network gateway."""

    def __init__(
        self,
        config: GatewayConfig | None = None,
        *,
        authorize: Authorizer | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.config = config or GatewayConfig()
        positive_ints = (
            self.config.max_body_bytes,
            self.config.max_replay_entries,
            self.config.max_principal_id_chars,
            self.config.max_action_chars,
            self.config.max_resource_chars,
            self.config.max_nonce_chars,
        )
        if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in positive_ints):
            raise ValueError("body, replay and context limits must be positive integers")
        for name, value, allow_zero in (
            ("max_clock_skew_seconds", self.config.max_clock_skew_seconds, True),
            ("replay_ttl_seconds", self.config.replay_ttl_seconds, False),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{name} must be a finite number")
            if value < 0 or (not allow_zero and value == 0):
                raise ValueError(f"{name} is outside its permitted range")
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
        fields = (
            (principal_id, self.config.max_principal_id_chars),
            (action, self.config.max_action_chars),
            (resource, self.config.max_resource_chars),
            (nonce, self.config.max_nonce_chars),
        )
        if any(not isinstance(value, str) or not value.strip() for value, _ in fields):
            return GuardDecision(False, "invalid_request_context")
        if any(len(value) > limit for value, limit in fields):
            return GuardDecision(False, "request_context_too_large")
        if not isinstance(body, bytes):
            return GuardDecision(False, "invalid_body_type")
        if len(body) > self.config.max_body_bytes:
            return GuardDecision(False, "payload_too_large")
        if isinstance(issued_at, bool) or not isinstance(issued_at, (int, float)) or not math.isfinite(issued_at):
            return GuardDecision(False, "invalid_timestamp")
        try:
            now = self.clock()
        except Exception:
            return GuardDecision(False, "clock_unavailable")
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now):
            return GuardDecision(False, "invalid_clock")
        now = float(now)
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
            if len(self._seen_nonces) >= self.config.max_replay_entries:
                return GuardDecision(False, "replay_capacity_exceeded")
            self._seen_nonces[nonce] = now + self.config.replay_ttl_seconds

        try:
            permitted = self.authorize(principal_id, action, resource)
        except Exception:
            with self._lock:
                self._seen_nonces.pop(nonce, None)
            return GuardDecision(False, "authorization_error")

        if permitted is not True:
            with self._lock:
                self._seen_nonces.pop(nonce, None)
            if permitted is False:
                return GuardDecision(False, "unauthorized")
            return GuardDecision(False, "invalid_authorization_response")

        return GuardDecision(True, "allowed")
