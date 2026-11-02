# Agent instructions

- Treat AIX as an extension layer; do not replace MCP, A2A, HTTP, JSON-RPC, or OpenAPI.
- AIX Core owns message semantics; AIX Codecs owns canonical serialization.
- Identity Trust owns identity and authentication contracts; Policy Engine owns authorization decisions.
- Never trust a caller-supplied principal unless a trusted upstream authenticator has verified it.
- Fail closed when authentication context or authorization is missing, invalid, denied, or unavailable.
- Enforce payload size, timestamp freshness, replay/idempotency and resource budgets.
- The in-memory replay cache is a single-process prototype, not distributed protection.
- Do not add network listeners until transport-specific threat models and negative tests exist.
- Do not claim production security or MCP/A2A conformance without reproducible evidence.
- Do not serialize private reasoning or chain-of-thought.
- License is pending review; do not add a license file or infer one.
- Run `python -m unittest discover -s tests -v` before proposing changes.
