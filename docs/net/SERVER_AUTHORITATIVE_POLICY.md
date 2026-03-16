Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: `policy.net.server_authoritative` over canonical net schemas + Session pipeline net stages.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Server Authoritative Policy

## Purpose
Define deterministic replication behavior where server is sole TruthModel executor and clients consume PerceivedModel-only updates.

## Core Contract

1. Truth authority:
   - Server executes deterministic tick pipeline and commits authoritative truth.
2. Client role:
   - Clients submit `intent_envelope` artifacts only.
   - Clients do not mutate truth.
3. Network payload scope:
   - Allowed: `perceived_delta`, `hash_anchor_frame`, `snapshot` metadata/reference.
   - Forbidden: raw TruthModel transmission over net path.

## Determinism Scope

1. Server determinism is mandatory:
   - identical inputs -> identical authoritative hash anchor sequence.
2. Client determinism requirement:
   - deterministic PerceivedModel delta apply + hash verification.
   - render-layer behavior is non-authoritative.
3. Timing:
   - network timing does not decide authoritative outcomes.

## Tick Output Rules

Per authoritative tick:

1. Server processes validated intent queue through canonical process pipeline.
2. Server emits `hash_anchor_frame`.
3. For each connected peer, server derives PerceivedModel via Observation Kernel and emits `perceived_delta`.
4. Every `snapshot_cadence_ticks` (policy extension), server emits `snapshot` reference metadata for resync.

## Snapshot and Delta

1. Snapshot cadence is policy-driven from `data/registries/net_replication_policy_registry.json`:
   - `policy.net.server_authoritative` extension `snapshot_cadence_ticks`.
2. `snapshot` artifact contains truth hash + payload reference, not inline truth payload.
3. `perceived_delta` contains peer-scoped payload reference and `perceived_hash`.

## Resync Strategy

Strategy ID: `resync.authoritative.snapshot`

1. Client detects mismatch (`refusal.net.resync_required`) or delta loss.
2. Client requests authoritative snapshot.
3. Client replaces local PerceivedModel cache from snapshot peer payload and resumes deltas.
4. Missing snapshot path refuses deterministically with `refusal.net.resync_snapshot_missing`.

## Pipeline Integration

Applies to multiplayer stage chain:

1. `stage.net_handshake`
2. `stage.net_sync_baseline`
3. `stage.net_join_world`

Rules:

1. `stage.net_sync_baseline` produces baseline summary + snapshot references.
2. `stage.net_join_world` validates policy/snapshot and supports deterministic midstream join for this policy.
3. Non-authoritative policies currently refuse in these stages until implemented.

## Anti-Cheat Hooks (MP-4)

Enabled via anti-cheat policy/module registries:

1. `ac.module.input_integrity`
2. `ac.module.sequence_integrity`
3. `ac.module.authority_integrity`
4. `ac.module.state_integrity`
5. `ac.module.behavioral_detection` (event-only in this phase)

Actions are policy-driven (`audit|refuse|terminate|throttle`) and deterministic.

## Refusal Codes

1. `refusal.net.envelope_invalid`
2. `refusal.net.sequence_violation`
3. `refusal.net.replay_detected`
4. `refusal.net.authority_violation`
5. `refusal.net.resync_required`
6. `refusal.net.resync_snapshot_missing`
7. `refusal.net.join_snapshot_invalid`
8. `refusal.net.join_policy_mismatch`

## Limitations (Intentional for MP-4)

1. No client prediction / rollback.
2. No lag compensation.
3. Single-shard authoritative runtime only (`shard.0`).
4. Snapshot references are file-artifact based for now.

## Cross-References

- `docs/net/REPLICATION_POLICIES.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/net/EPISTEMICS_OVER_NETWORK.md`
- `docs/contracts/refusal_contract.md`
- `data/registries/net_replication_policy_registry.json`
- `data/registries/net_resync_strategy_registry.json`
