Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Derived from `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `docs/compat/ENDPOINT_DESCRIPTORS.md`, `src/server/net/loopback_transport.py`, and `src/client/local_server/local_server_controller.py`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CAP-NEG-2 Retro Audit

## Scope
- Existing client/server loopback handshake path
- Existing negotiation record production
- Existing read-only compatibility fallback
- Existing proof-anchor integration

## Findings
- Deterministic endpoint negotiation already exists in `src/compat/capability_negotiation.py`.
- Loopback transport already refuses connections when endpoint negotiation fails.
- Negotiation record hashes are already included in server proof anchors.
- Read-only compatibility mode already maps to `law.observer.default`, but mutation refusal was not explicit at the server intent boundary.
- Handshake behavior is implemented, but the protocol surface is not yet documented as a reusable handshake contract and does not yet have dedicated handshake-message schemas.
- Client loopback handling is embedded in local-singleplayer orchestration instead of a reusable client-side handshake surface.

## Required CAP-NEG-2 Additions
- Canonical handshake doctrine and message flow
- `handshake_message` and `compat_refusal` schemas
- Reusable negotiation and handshake engine surfaces
- Explicit read-only mutation refusal on the authoritative server path
- Replay tooling for negotiation records
- RepoX/AuditX/TestX coverage for mandatory negotiation and read-only enforcement
