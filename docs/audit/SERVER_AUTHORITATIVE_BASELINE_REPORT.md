Status: DERIVED
Version: 1.0.0
Last Updated: 2026-02-15
Scope: MP-4/9 server-authoritative replication baseline
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Server-Authoritative Baseline Report

## Purpose
This report records the MP-4 baseline for `policy.net.server_authoritative` with deterministic replication contracts and PerceivedModel-only transmission.

## Canon and Contract Alignment
- Canon sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`.
- Net contracts: `docs/net/SERVER_AUTHORITATIVE_POLICY.md`, `docs/net/REPLICATION_POLICIES.md`, `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`.
- Refusal contract: `docs/contracts/refusal_contract.md`.

## Snapshot Cadence Policy
- Policy ID: `policy.net.server_authoritative`.
- Registry source: `data/registries/net_replication_policy_registry.json`.
- Cadence field: `extensions.snapshot_cadence_ticks`.
- MP-4 baseline value: `2` ticks.
- Runtime behavior:
  - Snapshot metadata artifact validated via `net_snapshot`.
  - Snapshot payload stored as canonical artifact reference.
  - `truth_snapshot_hash` transmitted, never raw TruthModel payload.

## Perceived Delta Structure Summary
- Outbound state uses Observation Kernel derivation per client/lens/law/authority context.
- Delta metadata schema: `net_perceived_delta`.
- Canonical fields:
  - `perceived_delta_id`
  - `tick`
  - `peer_id`
  - `lens_id`
  - `epistemic_scope_id`
  - `payload_ref`
  - `perceived_hash`
- Determinism properties:
  - Canonical serialization for payload and metadata.
  - Stable ordering by `(tick, peer_id, perceived_delta_id)`.
  - Perceived hash verification on apply.

## Resync Strategy
- Strategy ID: `resync.authoritative.snapshot`.
- Trigger conditions:
  - Perceived hash mismatch.
  - Join requiring baseline state.
- Procedure:
  1. Request authoritative snapshot.
  2. Reset client perceived cache.
  3. Apply snapshot-perceived state for peer.
  4. Continue from authoritative tick stream.
- Deterministic refusal path:
  - `refusal.net.resync_snapshot_missing` when snapshot data is unavailable.
  - `refusal.net.join_snapshot_invalid` for invalid/missing join snapshot.
  - `refusal.net.join_policy_mismatch` for negotiated policy mismatch.

## Anti-Cheat Modules Enabled (Policy-Driven)
- Base policy: `policy.ac.casual_default` in MP-4 tests.
- Integrated module hooks:
  - `ac.module.input_integrity`
  - `ac.module.sequence_integrity`
  - `ac.module.authority_integrity`
  - `ac.module.state_integrity`
  - `ac.module.behavioral_detection`
- Event artifact schema: `net_anti_cheat_event`.
- Enforcement behavior remains policy-driven and explicit (audit/refuse/terminate as configured).

## Determinism Validation Summary
- Deterministic checks implemented and passing in strict subset:
  - `testx.net.authoritative_two_clients_determinism`
  - `testx.net.authoritative_snapshot_join_midstream`
  - `testx.net.authoritative_resync_snapshot`
  - `testx.net.authoritative_refuse_invalid_envelope`
  - `testx.net.authoritative_no_truth_over_net`
  - `testx.net.pipeline_net_handshake_stage_authoritative`
- Guardrails:
  - RepoX invariants:
    - `INV-AUTHORITATIVE-NO-TRUTH-TRANSMISSION`
    - `INV-AUTHORITATIVE-USES-PERCEIVED-ONLY`
  - AuditX analyzer:
    - `E4_AUTHORITATIVE_TRUTH_LEAK`

## Known Limitations
- No client prediction or rollback smoothing.
- No lag compensation.
- No SRZ hybrid replication in this phase.
- No transport-level encryption/signature enforcement beyond existing policy stubs.
- Snapshot payload transfer remains artifact-reference-based, not full transport implementation.

## Extension Notes
- Future prompts can extend:
  - snapshot cadence policy tables
  - delta compression strategies (must preserve canonical hashing semantics)
  - anti-cheat module coverage and action policies
  - SRZ distributed authority replication profile integration
