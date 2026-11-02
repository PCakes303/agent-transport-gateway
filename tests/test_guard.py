import unittest

from gateway_guard import GatewayConfig, GatewayGuard


class GatewayGuardTests(unittest.TestCase):
    def setUp(self):
        self.now = [1_800_000_000.0]
        self.guard = GatewayGuard(
            GatewayConfig(max_body_bytes=8, max_clock_skew_seconds=30, replay_ttl_seconds=60),
            authorize=lambda principal, action, resource: True,
            clock=lambda: self.now[0],
        )

    def request(self, **overrides):
        values = dict(
            principal_id="agent:alpha",
            action="aix.task.submit",
            resource="task:123",
            body=b'{"ok":1}',
            issued_at=self.now[0],
            nonce="nonce-1",
        )
        values.update(overrides)
        return self.guard.check(**values)

    def test_valid_request_is_allowed(self):
        decision = self.request()
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.code, "allowed")

    def test_oversized_body_is_denied(self):
        self.assertEqual(self.request(body=b"x" * 9).code, "payload_too_large")

    def test_stale_request_is_denied(self):
        self.assertEqual(self.request(issued_at=self.now[0] - 31).code, "stale_request")

    def test_replayed_nonce_is_denied(self):
        self.assertTrue(self.request().allowed)
        self.assertEqual(self.request().code, "replay_detected")

    def test_expired_nonce_can_be_reused(self):
        self.assertTrue(self.request().allowed)
        self.now[0] += 61
        self.assertTrue(self.request().allowed)

    def test_missing_authorizer_fails_closed(self):
        guard = GatewayGuard(clock=lambda: self.now[0])
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="n"
        ).code, "authorizer_unavailable")

    def test_denied_authorization_is_denied(self):
        guard = GatewayGuard(authorize=lambda *_: False, clock=lambda: self.now[0])
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="n"
        ).code, "unauthorized")

    def test_authorizer_exception_fails_closed(self):
        def broken(*_):
            raise RuntimeError("policy service unavailable")
        guard = GatewayGuard(authorize=broken, clock=lambda: self.now[0])
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="n"
        ).code, "authorization_error")


    def test_replay_cache_capacity_is_bounded(self):
        guard = GatewayGuard(
            GatewayConfig(max_body_bytes=8, max_clock_skew_seconds=30,
                          replay_ttl_seconds=60, max_replay_entries=1),
            authorize=lambda *_: True, clock=lambda: self.now[0]
        )
        self.assertTrue(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="first"
        ).allowed)
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="second"
        ).code, "replay_capacity_exceeded")

    def test_oversized_context_is_denied(self):
        self.assertEqual(self.request(nonce="n" * 257).code, "request_context_too_large")

    def test_boolean_timestamp_is_rejected(self):
        self.assertEqual(self.request(issued_at=True).code, "invalid_timestamp")

    def test_nonfinite_clock_is_rejected(self):
        guard = GatewayGuard(authorize=lambda *_: True, clock=lambda: float("nan"))
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="n"
        ).code, "invalid_clock")

    def test_clock_exception_fails_closed(self):
        def broken_clock():
            raise RuntimeError("clock unavailable")
        guard = GatewayGuard(authorize=lambda *_: True, clock=broken_clock)
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="n"
        ).code, "clock_unavailable")

    def test_truthy_non_boolean_authorization_response_is_rejected(self):
        guard = GatewayGuard(authorize=lambda *_: "false", clock=lambda: self.now[0])
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="n"
        ).code, "invalid_authorization_response")

    def test_nonfinite_config_values_are_rejected(self):
        with self.assertRaises(ValueError):
            GatewayGuard(GatewayConfig(max_clock_skew_seconds=float("nan")))
        with self.assertRaises(ValueError):
            GatewayGuard(GatewayConfig(replay_ttl_seconds=float("inf")))

    def test_noninteger_replay_capacity_is_rejected(self):
        with self.assertRaises(ValueError):
            GatewayGuard(GatewayConfig(max_replay_entries=1.5))

    def test_invalid_context_is_denied(self):
        self.assertEqual(self.request(principal_id=" ").code, "invalid_request_context")

    def test_invalid_body_type_is_denied(self):
        self.assertEqual(self.request(body='{"ok":1}').code, "invalid_body_type")

    def test_overflowing_integer_timestamp_is_rejected(self):
        self.assertEqual(self.request(issued_at=10**10000).code, "invalid_timestamp")

    def test_overflowing_integer_clock_is_rejected(self):
        guard = GatewayGuard(authorize=lambda *_: True, clock=lambda: 10**10000)
        self.assertEqual(guard.check(
            principal_id="agent:alpha", action="read", resource="r",
            body=b"{}", issued_at=self.now[0], nonce="n"
        ).code, "invalid_clock")

    def test_overflowing_integer_timing_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            GatewayGuard(GatewayConfig(max_clock_skew_seconds=10**10000))


if __name__ == "__main__":
    unittest.main()
