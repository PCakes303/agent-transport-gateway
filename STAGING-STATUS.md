# Repository 13 deployment and audit status

**Repository:** [PCakes303/agent-transport-gateway](https://github.com/PCakes303/agent-transport-gateway)  
**Audited baseline:** `1b2e5873f05364fc0c8f2c124bc76c640eeb3096`  
**Baseline CI:** [Run 41427827799](https://github.com/PCakes303/agent-transport-gateway/actions/runs/41427827799) — success on Python 3.10, 3.11 and 3.12  
**Staging source:** `provisioning/staged/agent-transport-gateway/` in the master repository.

## Current deployment record

The public remote exists and is authoritative for current implementation. The historical 15-file scaffold deployment and CI run are provenance, not proof of current staging-to-remote byte parity. Refresh path/blob-SHA parity before portfolio sign-off.

## Remediation in progress

The request guard now validates finite configuration and timestamps, bounds principal/action/resource/nonce lengths, caps replay-cache entries, fails closed on replay-cache exhaustion and accepts only explicit boolean `True` from the authorization callback. The cache remains process-local and volatile.

## Remaining verification

- Verify GitHub About description, homepage and topics separately; the master metadata guide contains proposals, not applied settings.
- Verify GitHub private vulnerability reporting/security advisory configuration; SECURITY.md records that no dedicated private reporting address is published.
- Verify branch rulesets/protection, Actions permissions, secret scanning, push protection and dependency alerts.
- Refresh staging-to-remote path and blob-SHA parity against current `main`.
- Retain pending license status until an explicit repository/artifact licensing decision is approved.

## Maturity and limitations

This is an experimental transport-neutral request guard, not a network gateway. It does not authenticate principals, verify cryptographic signatures, validate AIX schemas, provide HTTP/MCP/A2A adapters, supply a production authorization service, or provide durable/distributed replay storage. No production security or protocol-conformance claim is made.
