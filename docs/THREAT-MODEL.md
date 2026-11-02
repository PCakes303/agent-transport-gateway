# Threat Model

## Assets

- Authenticated principal context
- AIX message payloads and task metadata
- Authorization decisions and policy versions
- Replay/idempotency state
- Transport availability and resource budgets
- Audit evidence

## Threats and controls

| Threat | Initial control | Remaining limitation |
|---|---|---|
| Unauthenticated principal spoofing | Explicit trusted-authentication precondition | No authenticator is implemented |
| Unauthorized action | Fail-closed authorization callback | No production policy adapter |
| Oversized payload | Configurable maximum body bytes | No network ingress or streaming limits |
| Stale request | Configurable timestamp skew | Clock synchronization is an operational dependency |
| Replay | Process-local nonce cache | Not shared or durable across workers/restarts |
| Malformed AIX message | Future schema/codec validation boundary | Not implemented in initial guard |
| Transport denial of service | Body limit | Rate limits, quotas and connection budgets remain future work |
| Protocol confusion | Explicit adapter contracts | No MCP/A2A adapters yet |

## Non-goals

This scaffold does not claim TLS termination, credential issuance, signature verification, authorization enforcement at a remote resource, distributed replay defense, or production hardening.
