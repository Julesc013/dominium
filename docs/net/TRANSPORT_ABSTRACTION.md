Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, and `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Transport Abstraction

## Purpose
Define the pluggable multiplayer transport boundary used by deterministic protocol artifacts.

## Core Invariants
- Transport is pluggable and must not encode gameplay semantics.
- Protocol payloads are schema-validated and canonical-serialized before transport.
- Transport timing may change delivery latency but must not change authoritative truth outcomes.
- Policy selection is data-driven (`policy_id`), never hardcoded mode branches.
- Refusals are explicit and deterministic (`docs/contracts/refusal_contract.md`).

## Transport Types
Canonical transport IDs:
1. `transport.loopback`
2. `transport.tcp` (optional implementation)
3. `transport.udp` (optional implementation stub)

`transport.loopback` is the required deterministic baseline for test harnesses and single-process multi-peer simulation.

## Interface Contract
Transport implementations must expose:
1. `transport_id`
2. `connect(endpoint)`
3. `accept()`
4. `send(message_bytes)`
5. `recv()`
6. `close()`

`recv()` behavior:
- May be non-blocking.
- Must not inject nondeterministic decisions into protocol acceptance/refusal logic.

## Protocol Framing Contract
Wire framing occurs at protocol layer, not gameplay layer:
1. Protocol wraps payloads in `net_proto_message`.
2. Payload hashes are canonical (`tools/xstack/compatx/canonical_json.py`).
3. Message sequence is monotonic per connection.
4. UTF-8 canonical JSON framing is the v1 baseline.

## Reliability Semantics
- Reliability and ordering guarantees are expressed by `replication_policy_id` + protocol behavior.
- Transport layer does not override deterministic ordering rules from policy registries.
- Replay and sequence integrity checks remain policy-driven (`anti_cheat_policy_id` + module registry).

## Determinism Boundary
Authoritative determinism boundary:
1. `IntentEnvelope` ordering
2. Tick scheduling (`read -> propose -> resolve -> commit`)
3. Hash anchor validation

Transport nondeterminism (packet delay, batching, retries) must resolve into explicit protocol outcomes:
- accept
- refuse with deterministic reason code
- resync-required artifact

## Cross-References
- `docs/net/MULTIPLAYER_MODEL_OVERVIEW.md`
- `docs/net/REPLICATION_POLICIES.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/net/ANTI_CHEAT_POLICY_FRAMEWORK.md`
- `docs/net/EPISTEMICS_OVER_NETWORK.md`
- `schemas/net_proto_message.schema.json`
- `schemas/net_handshake.schema.json`

## TODO
- Add transport capability matrix (MTU, fragmentation, partial reliability) as policy metadata.
- Add secure transport negotiation hooks linked to SecureX policies.
