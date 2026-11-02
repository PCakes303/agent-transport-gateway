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

    def test_invalid_context_is_denied(self):
        self.assertEqual(self.request(principal_id=" ").code, "invalid_request_context")

    def test_invalid_body_type_is_denied(self):
        self.assertEqual(self.request(body='{"ok":1}').code, "invalid_body_type")


if __name__ == "__main__":
    unittest.main()
