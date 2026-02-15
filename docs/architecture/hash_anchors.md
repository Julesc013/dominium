Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0 and SessionX SRZ scheduler outputs.

# Hash Anchors v1

## Purpose
Define deterministic hash-anchor formulas used by SRZ scheduling and run-meta artifacts.

## Canonicalization
- Serializer: canonical JSON (`tools/xstack/compatx/canonical_json.py`)
- UTF-8 encoding
- Sorted object keys
- Stable list ordering from scheduler/registry rules

## PerTickHash
Formula:
`H(canonical(truth_subset + active_shards + pack_lock_hash + registry_hashes + last_tick_hash))`

Included inputs:
- authoritative Truth subset from UniverseState
- active shard summary (`shard_id`, ownership counts, last hash anchor)
- lock/registry identity (`pack_lock_hash`, registry hashes)
- previous tick hash (`last_tick_hash`)

Excluded inputs:
- wall-clock timestamps
- duration metrics
- non-authoritative presentation data

## CheckpointHash
- Frequency: every `N` scheduler ticks
- `N` comes from policy input when present, else default `4`

Formula:
`H(canonical(scheduler_tick + tick_hash + previous_checkpoint_hash + composite_hash))`

## CompositeHash
Multi-shard compatible formula:
`H(canonical(sorted(shard_id + shard_hash)))`

v1 runtime note:
- single-shard runtime computes CompositeHash with one active shard (`shard.0`)
- logical shard harness variation does not change authoritative composite in v1

## Artifact Locations
- Script run result payload:
  - `tick_hash_anchors`
  - `checkpoint_hashes`
  - `composite_hash`
- Run-meta file:
  - `saves/<save_id>/run_meta/<run_id>.json`

## Example (Abbreviated)
```json
{
  "tick_hash_anchors": [
    {
      "scheduler_tick": 1,
      "submission_tick": 0,
      "simulation_tick": 1,
      "tick_hash": "f4f8...",
      "composite_hash": "2e31..."
    }
  ],
  "checkpoint_hashes": [],
  "composite_hash": "2e31..."
}
```

## TODO
- Add hash-partition mapping to broader engine replay partitions.
- Add checkpoint retention policy for long sessions.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/architecture/srz_contract.md`
- `docs/architecture/deterministic_parallelism.md`
- `docs/architecture/session_lifecycle.md`
