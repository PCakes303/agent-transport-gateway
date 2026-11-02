# Transport Gateway Contract

## Scope

The gateway mediates requests between authenticated callers, policy decisions, AIX messages and established transports. It must not redefine AIX semantics or replace MCP, A2A, HTTP, JSON-RPC or OpenAPI.

## Request guard

A request guard receives:
- a principal identifier established by a trusted authentication layer;
- an action and resource identifier for authorization;
- raw request bytes;
- a timestamp;
- a unique nonce or idempotency token.

It rejects missing context, oversized bodies, stale timestamps, replayed nonces, missing authorizers, denied decisions and authorization errors.

## Trust boundaries

The guard does not authenticate the principal. It assumes its caller has already established identity. The guard must not accept an unverified principal from user-controlled headers or message fields.

The authorization callback must be backed by the policy-engine contract. A missing or failing callback denies the request.

## Replay behavior

The initial implementation uses an in-memory, process-local nonce cache for tests and single-process experimentation. It is not sufficient for a multi-worker or multi-host gateway. A production adapter must use atomic shared nonce reservation, bounded retention, and documented behavior under store failure.

## Protocol adapters

Future adapters map transport-specific request and response envelopes to the AIX Core message contract and AIX Codecs serialization. Each adapter must preserve protocol-native error, cancellation, timeout and retry semantics. A2A Agent Cards are published only when a real endpoint exists.

## Error model

Deny decisions use stable machine-readable codes. They must not leak secrets, authentication material, policy internals or private model reasoning.
