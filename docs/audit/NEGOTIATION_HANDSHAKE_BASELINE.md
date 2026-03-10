Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Derived from `docs/compat/NEGOTIATION_HANDSHAKES.md`, `src/compat/handshake/handshake_engine.py`, `src/server/net/loopback_transport.py`, and `src/client/net/loopback_client.py`.

# Negotiation Handshake Baseline

## Protocol Flow
- `client_hello` carries the client `EndpointDescriptor`.
- `server_hello` carries the server `EndpointDescriptor`.
- `negotiation_result` carries the deterministic `NegotiationRecord`.
- `ack` confirms or refuses the negotiated mode.
- `session_begin` binds the connection to the chosen contract bundle hash and pack lock hash.

## Read-Only Enforcement
- `compat.read_only` binds to `law.observer.default`.
- Authoritative mutation is refused at the server intent boundary for read-only connections.
- The negotiated mode is stored in connection metadata, proof anchors, and handshake logs.

## Proof Integration
- Negotiation record hashes and endpoint descriptor hashes are included in proof anchors.
- Replay tooling re-runs negotiation from the recorded descriptors and validates the hash.

## MVP Scope
- Local loopback client/server is covered.
- IPC attach uses the same handshake engine as a stub surface.
- No simulation semantics changed; CAP-NEG-2 formalizes and enforces interoperability behavior.
