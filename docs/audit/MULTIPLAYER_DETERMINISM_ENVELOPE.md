Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Multiplayer Determinism Envelope

Status: DERIVED BASELINE  
Last Updated: 2026-02-16

## Scope
This document defines the multiplayer determinism envelope for:

- `policy.net.lockstep`
- `policy.net.server_authoritative`
- `policy.net.srz_hybrid`

The envelope is normative for TestX regression locks and CI verification lanes.

## Deterministic Inputs
For any multiplayer run, the deterministic input set is:

- `SessionSpec` (including network policy IDs and authority context)
- `pack_lock_hash`
- registry hash map from `lockfile.json`
- deterministic RNG roots
- `shard_map_id`
- deterministic disorder profile (for test harnesses only)
- scripted intent stream (ordered)

## Deterministic Invariants
Given identical deterministic inputs:

- server-side authoritative truth evolution is identical
- per-tick hash anchors are identical
- final composite hash anchor is identical
- anti-cheat event fingerprints are identical
- refusal payloads are identical (except non-canonical timing metadata)

The invariants hold independent of:

- message arrival ordering
- packet duplication patterns
- packet drop patterns when deterministic repair/resync is applied
- worker/thread count within supported deterministic scheduler configurations
- client count, when intent stream and authority bindings are equivalent

## Exclusions
The following fields are excluded from canonical equivalence:

- wall-clock timestamps
- non-canonical run-meta timing measurements

No exclusion is allowed for truth-affecting state, policy IDs, hashes, or refusal codes.

## Policy Notes
### `policy.net.lockstep`
- Deterministic ordering key: `(submission_tick, target_shard_id, peer_id, deterministic_sequence_number, intent_id)`.
- Tick intent ledger is canonical.
- Resync uses deterministic replay from checkpoint + tick intent lists.

### `policy.net.server_authoritative`
- Server is sole TruthModel executor.
- Clients receive only PerceivedModel deltas and hash anchors.
- Resync path is deterministic snapshot + delta replay.

### `policy.net.srz_hybrid`
- Shard routing is deterministic from shard map + envelope.
- Per-shard hashes compose into deterministic composite anchor.
- Resync path is deterministic shard-snapshot based for scoped clients.

## Regression Lock Contract
`data/regression/multiplayer_baseline.json` is the lock artifact for:

- policy A/B/C anchor baselines
- ranked handshake acceptance/refusal baselines
- anti-cheat fingerprint baselines for adversarial cases

Baseline updates require commit message tag: `MULTIPLAYER-REGRESSION-UPDATE`.
