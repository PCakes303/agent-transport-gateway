# Agent Transport Gateway

**Portfolio position:** Repository 13 / 29 public  
**Layer:** Protocols  
**Maturity:** prepared scaffold; standalone remote not yet created  
**Dependencies:** AIX Core, AIX Codecs, Agent Identity & Trust, Agent Policy Engine

## Mission

Provide a controlled boundary between AIX messages and established transports such as HTTP, MCP and A2A. The gateway is an integration layer, not a replacement protocol. It must preserve upstream protocol semantics while enforcing explicit size, freshness, replay and authorization checks at the gateway boundary.

## Initial implementation

This first scaffold is deliberately transport-neutral. It provides an experimental request guard that can be embedded by a future HTTP/MCP/A2A adapter. It does not start a network listener, authenticate callers, issue credentials, verify signatures, or claim production gateway security.

## Security invariants

- Authenticate the caller through a trusted identity integration before supplying a principal to the guard.
- Fail closed if authorization is unavailable, denies, or raises an error.
- Enforce payload-size and timestamp-freshness limits.
- Reject replayed nonces within the configured in-memory window.
- Treat in-memory replay state as single-process prototype behavior only.
- Keep AIX semantics in AIX Core and serialization in AIX Codecs.
- Never expose private model reasoning or chain-of-thought through transport messages.

## Run tests

Python 3.10+; standard library only.

```bash
python -m unittest discover -s tests -v
```

## Next gates

1. Deploy this scaffold to the standalone repository.
2. Integrate a pinned AIX Core schema and AIX Codecs canonical parser.
3. Add authenticated principal resolution through Agent Identity & Trust.
4. Add a policy-engine adapter with signed/versioned policy inputs.
5. Implement one HTTP adapter and protocol-specific MCP/A2A adapters.
6. Replace in-memory replay tracking with a bounded, shared, durable store for multi-instance deployment.
7. Add end-to-end negative security tests, fuzzing, load limits, and operational telemetry.

No production security, authentication, MCP/A2A conformance, or multi-node replay protection is claimed.
