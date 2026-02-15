Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: `docs/architecture/deterministic_parallelism.md` v1.0.0-draft
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0 and SessionX scheduler implementation in `tools/xstack/sessionx/scheduler.py`.

# Deterministic Parallelism v1

## Purpose
Define the scheduler invariants that keep authoritative outcomes deterministic across worker-count and proposal-order variation.

## Phase Model
Each scheduler tick executes exactly:
1. `read`
2. `propose`
3. `resolve`
4. `commit`

No authoritative mutation is allowed before `commit`.

## Proposal Construction
Input:
- validated intent envelopes (`schemas/intent_envelope.schema.json`)

Proposal fields:
- `priority`
- `entity_id`
- `process_id`
- `intent_sequence`
- `field_scope`

Worker-count handling:
- proposal generation order may vary deterministically in harness mode
- commit ordering never depends on proposal arrival order

## Resolve Ordering Rule
Canonical sort key:
`(priority, entity_id, process_id, intent_sequence)`

Conflict policy:
- key: `(entity_id, field_scope)`
- rule: `first_wins` after canonical sort
- dropped proposals are logged deterministically

## Commit Rule
- Only accepted proposals commit.
- Commit invokes process runtime mutation primitives.
- Commit produces deterministic hash anchors.

## Invariance Requirements
- Same inputs must yield identical:
  - per-tick hash anchors
  - checkpoint hashes
  - final composite hash
  - final authoritative state hash
- Worker-count variation (`workers=1` vs `workers=2`) must not change outcomes.
- Logical shard harness variation must not change single-shard authoritative outputs in v1.

## TestX Gates
STRICT includes:
- `testx.srz.hash_anchor_replay`
- `testx.srz.logical_two_shard_consistency`
- `testx.srz.worker_invariance`
- `testx.srz.target_shard_invalid_refusal`

## Example Resolve Ordering
```text
proposals (unsorted):
  p3: priority=40 entity=camera.main process=process.camera_move intent_sequence=3
  p1: priority=20 entity=time.control process=process.time_pause intent_sequence=1
  p2: priority=30 entity=camera.main process=process.camera_teleport intent_sequence=2

resolved canonical order:
  p1 -> p2 -> p3
```

## TODO
- Add fixed-tree deterministic reduction spec for future multi-shard merge.
- Add explicit commit proof artifacts per shard for SRZ networked mode.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/architecture/srz_contract.md`
- `docs/architecture/hash_anchors.md`
- `docs/contracts/refusal_contract.md`
