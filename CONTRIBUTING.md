# Contributing

Changes to gateway contracts require a threat-model update, compatibility analysis, and positive and negative tests.

Before submitting:

1. Read `AGENTS.md`, `SECURITY.md`, and `docs/TRANSPORT-CONTRACT.md`.
2. Add tests for deny paths, malformed input, replay, expiry and resource limits.
3. Run `python -m unittest discover -s tests -v`.
4. Document which identity and policy interfaces are real versus injected test doubles.
5. Do not claim authentication, authorization, protocol conformance or production readiness without evidence.

Use pull requests for reviewed changes. Never commit credentials, private keys, tokens or private operational material.
