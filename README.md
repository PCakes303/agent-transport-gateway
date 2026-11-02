# Agent Transport Gateway

**Layer:** Protocols  
**Maturity:** experimental request-guard scaffold deployed to the standalone public repository; Python 3.10–3.12 CI passing  
**Dependencies:** AIX Core, AIX Codecs, Agent Identity & Trust, Agent Policy Engine

## License status

The repository's code, documentation, schemas, examples, and other materials do not yet have an approved license decision. No root `LICENSE` file or GitHub license declaration is present. Reuse and redistribution rights must not be assumed; licensing remains pending repository-specific review.

## Mission

Provide a controlled boundary between AIX messages and established transports such as HTTP, MCP and A2A. The gateway is an integration layer, not a replacement protocol. It must preserve upstream protocol semantics while enforcing explicit size, freshness, replay and authorization checks at the gateway boundary.

## Initial implementation

This first scaffold is deliberately transport-neutral. It provides an experimental request guard that can be embedded by a future HTTP/MCP/A2A adapter. It does not start a network listener, authenticate callers, issue credentials, verify signatures, or claim production gateway security.

## Security invariants

- Authenticate the caller through a trusted identity integration before supplying a principal to the guard.
- Fail closed if authorization is unavailable, denies, or raises an error.
- Enforce payload-size and timestamp-freshness limits.
- Reject replayed nonces within the configured in-memory window.
- Bound the in-memory replay cache; treat it as single-process prototype behavior only.
- Keep AIX semantics in AIX Core and serialization in AIX Codecs.
- Never expose private model reasoning or chain-of-thought through transport messages.

## Run tests

Python 3.10+; standard library only.

```bash
python -m unittest discover -s tests -v
```

## Next gates

1. Integrate a pinned AIX Core schema and AIX Codecs canonical parser.
2. Add authenticated principal resolution through Agent Identity & Trust.
3. Add a policy-engine adapter with signed/versioned policy inputs.
4. Implement one HTTP adapter and protocol-specific MCP/A2A adapters.
5. Replace the bounded in-memory replay cache with a shared, durable store for multi-instance deployment.
6. Add end-to-end negative security tests, fuzzing, load limits, and operational telemetry.

No production security, authentication, MCP/A2A conformance, or multi-node replay protection is claimed.
