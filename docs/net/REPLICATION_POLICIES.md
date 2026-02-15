Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to canonical multiplayer schema/registry contracts and `docs/canon/constitution_v1.md`.

# Replication Policies

## Purpose
Define policy IDs for canonical multiplayer replication behaviors over shared primitives.

## Policy IDs

1. `policy.net.lockstep`
2. `policy.net.server_authoritative`
3. `policy.net.srz_hybrid`

## Implementation Status (MP-4)

1. `policy.net.lockstep`: implemented as deterministic module baseline in MP-3.
2. `policy.net.server_authoritative`: implemented in MP-4 with PerceivedModel delta + snapshot resync path.
3. `policy.net.srz_hybrid`: declared contract only; implementation pending later prompts.

## Transmission Contracts

### `policy.net.lockstep`

1. Required artifacts:
   - `tick_intent_list`
   - `hash_anchor_frame`
2. Optional artifacts:
   - perceived deltas for spectator/observer acceleration.
3. Determinism:
   - Truth commit depends on deterministic envelope ordering only.
4. Resync:
   - `resync.lockstep.replay_intents`

### `policy.net.server_authoritative`

1. Required artifacts:
   - `perceived_delta`
   - snapshot cadence references
   - `hash_anchor_frame`
2. Truth authority:
   - Server commits; clients consume filtered perceived updates.
3. Resync:
   - `resync.authoritative.snapshot`
4. Snapshot cadence:
   - policy-driven via `data/registries/net_replication_policy_registry.json` extensions (`snapshot_cadence_ticks`).

### `policy.net.srz_hybrid`

1. Required artifacts:
   - shard-routed `intent_envelope`
   - shard/composite hash anchors
   - perceived deltas
2. Truth authority:
   - Deterministic SRZ ownership map per shard.
3. Resync:
   - `resync.hybrid.shard_snapshot`

## Resync/Repair Rules

1. Resync strategy is policy-declared (no implicit fallback).
2. Hash divergence must trigger explicit `refusal.net.resync_required`.
3. Repair steps must be deterministic and auditable through stage/run logs.

## Example Policy Matrix

| policy_id | tx_primary | tx_secondary | hash_anchor_required | resync_strategy_id |
|---|---|---|---|---|
| policy.net.lockstep | tick_intent_list | perceived_delta (optional) | yes | resync.lockstep.replay_intents |
| policy.net.server_authoritative | perceived_delta | snapshot/delta refs | yes | resync.authoritative.snapshot |
| policy.net.srz_hybrid | intent_envelope (shard-routed) | perceived_delta | yes | resync.hybrid.shard_snapshot |

## Cross-References

- `data/registries/net_replication_policy_registry.json`
- `data/registries/net_resync_strategy_registry.json`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/contracts/refusal_contract.md`

## TODO

- Add ranked/esports policy envelope thresholds for packet loss tolerance as non-canonical guidance.
