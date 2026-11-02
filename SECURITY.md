# Security policy

This repository begins as a transport-neutral request guard. It is not yet a network gateway and is not a production security boundary.

The guard accepts a principal identifier from its caller. A future transport adapter MUST obtain that principal from a trusted authentication layer; arbitrary request headers or unverified message fields are not proof of identity.

The authorization callback is an integration seam. A production adapter MUST connect it to an authenticated, policy-versioned decision service and fail closed on timeout or error.

The in-memory replay cache is process-local and volatile. It does not prevent replay across workers, hosts, restarts, or regions. Production deployment requires a bounded shared store with atomic nonce reservation and retention policy.

Payload size and clock-skew checks reduce selected risks but do not replace schema validation, signature verification, TLS, rate limiting, quotas, sandboxing, or protocol-specific threat analysis.

Report suspected vulnerabilities privately to the maintainer. Do not publish exploit details or secrets in public issues.
