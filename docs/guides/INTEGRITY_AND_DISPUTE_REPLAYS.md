Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Integrity & Dispute Replays (DIST2)

This guide defines deterministic integrity checkpoints, witness verification,
and dispute replay bundles. These mechanisms are advisory and audit-only: they
never mutate authoritative state and never bypass law/capability gates.

## Integrity Checkpoints

Checkpoint fields:
- `shard_id`
- `act_tick`
- `partition_ids[]` (DET0 partitions)
- `hash_values[]` (authoritative-only)
- `schema_versions[]`
- `mod_graph_hash`
- `engine_build_id`, `game_build_id`

Rules:
- Hashes are deterministic and stable across platforms.
- Only authoritative state contributes to hashes.
- Presentation or derived state is excluded.

## Scheduling

Checkpoints are event-driven:
- fixed ACT intervals, or
- significant events (configurable)

Scheduling uses deterministic ACT time only. No wall-clock timing.

## Witness Verification (Optional)

Witness nodes:
- receive inputs and checkpoints,
- recompute hashes independently,
- report mismatches deterministically.

Witnesses are advisory only and cannot override authoritative state.

## Dispute Bundles

Bundle content (minimum):
- snapshot reference or hash
- command/input stream hash
- RNG seed
- schema/version hashes
- mod graph hash
- checkpoint series

Bundles must be reproducible offline. They must not leak hidden information.

## Tooling Workflow

The dispute replay inspector:
- loads a dispute bundle,
- replays deterministically,
- verifies checkpoint hashes,
- reports first divergence.

Tools must never mutate state or bypass epistemic boundaries.

## Forbidden

- nondeterministic hashing or ordering
- silent admin overrides
- cross-shard state leaks in bundles
- witness nodes treated as authoritative