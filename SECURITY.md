# Security Policy

This repository is an experimental transport-neutral request guard. It is not a network gateway, authenticator, policy service, or production security boundary.

## Reporting

Do not publish exploitable vulnerabilities, credentials, private keys, or sensitive operational data in public issues. Use GitHub private vulnerability reporting or a private security advisory if enabled for this repository. A dedicated private reporting address is not published here; if private reporting is unavailable, the owner must configure an owner-approved private channel before production use.

## Trust and operational limits

- The guard accepts a principal identifier from its caller; it does not authenticate that principal. A trusted upstream authentication layer is mandatory.
- The authorization callback is an integration seam, not a policy engine. Only an explicit boolean `True` is accepted as an allow result.
- The replay cache is bounded and process-local. It does not prevent replay across workers, hosts, restarts, or regions; capacity exhaustion fails closed.
- Body and context length limits, timestamp validation, and a bounded replay cache do not replace schema validation, signature verification, TLS, rate limiting, quotas, durable shared replay state, or protocol-specific threat analysis.
- Do not add network listeners or enable workload execution until authentication, authorization, schema validation, replay protection, rate limits, audit integration, and protocol-specific security controls are implemented and reviewed.
