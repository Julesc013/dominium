Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: `docs/architecture/srz_contract.md` v1.0.0-draft
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0, `schemas/srz_shard.schema.json` v1.0.0, and `schemas/intent_envelope.schema.json` v1.0.0.

# SRZ Contract v1

## Purpose
Define the SRZ (Simulation Responsibility Zone) execution contract used by SessionX scheduling.
SRZ v1 is single-process and single-authoritative-shard, but all inputs/outputs are structured for future multi-shard expansion.

## Runtime Scope (v1)
- Runtime mode: `single_shard`
- Authoritative shard: `shard.0`
- Networking: not implemented
- Cross-shard transport: not implemented
- Intent routing: envelope format is active now, target shard must be `shard.0`

## Source of Truth
- `schemas/srz_shard.schema.json` (v1.0.0)
- `schemas/intent_envelope.schema.json` (v1.0.0)
- `tools/xstack/sessionx/srz.py`
- `tools/xstack/sessionx/scheduler.py`
- `tools/xstack/srz_status.py`

## Shard Definition
Schema contract (`schemas/srz_shard.schema.json`):
- `schema_version`
- `shard_id`
- `authority_origin`
- `region_scope`
- `active`
- `parent_shard_id`
- `compatibility_version`

Runtime extension fields (not part of schema validation payload):
- `owned_entities` (stable entity IDs)
- `owned_regions` (stable interest-region IDs)
- `process_queue` (deterministic queue snapshot)
- `last_hash_anchor` (last committed per-tick hash)

## Ownership Rules (v1)
- `shard.0` owns all authoritative entities and interest regions.
- Ownership is derived deterministically from UniverseState, not from thread timing.
- `tools/xstack/srz_status` reports ownership counts and `last_hash_anchor`.
- STRICT tests verify single-shard ownership remains stable.

## Intent Envelope Contract
Schema contract (`schemas/intent_envelope.schema.json`):
- `schema_version`
- `envelope_id`
- `authority_origin`
- `source_shard_id`
- `target_shard_id`
- `intent_id`
- `payload` (`process_id`, `inputs`)
- `deterministic_sequence_number`
- `submission_tick`

Invariants:
- Envelope ordering is deterministic by `(deterministic_sequence_number, envelope_id)`.
- `target_shard_id != "shard.0"` refuses with `SHARD_TARGET_INVALID`.
- Envelope validation is strict (unknown top-level fields refused).

## Scheduling Contract
Scheduler phase order is fixed:
1. `read`
2. `propose`
3. `resolve`
4. `commit`

Rules:
- `read`: snapshot-only, no mutation.
- `propose`: derive proposal rows from envelopes, no Truth mutation.
- `resolve`: sort by `(priority, entity_id, process_id, intent_sequence)` and apply conflict policy (`first_wins` by field scope).
- `commit`: apply accepted proposals through process runtime only.

## Refusal Codes Used by SRZ v1
- `SHARD_TARGET_INVALID`
- `SRZ_SHARD_INVALID`
- `PROCESS_INPUT_INVALID`

See also:
- `docs/contracts/refusal_contract.md`

## Example: Shard (Schema View)
```json
{
  "schema_version": "1.0.0",
  "shard_id": "shard.0",
  "authority_origin": "client",
  "region_scope": {
    "object_ids": [
      "camera.main"
    ],
    "spatial_bounds": null
  },
  "active": true,
  "parent_shard_id": null,
  "compatibility_version": "1.0.0"
}
```

## Example: Intent Envelope
```json
{
  "schema_version": "1.0.0",
  "envelope_id": "env.shard.0.00000001",
  "authority_origin": "client",
  "source_shard_id": "shard.0",
  "target_shard_id": "shard.0",
  "intent_id": "intent.camera.teleport.0001",
  "payload": {
    "process_id": "process.camera_teleport",
    "inputs": {
      "target_object_id": "object.earth"
    }
  },
  "deterministic_sequence_number": 1,
  "submission_tick": 0
}
```

## Future Distributed Plan (Non-Normative)
- Add additional active shards with explicit ownership transfer contracts.
- Add envelope transport/proof artifacts for cross-node commit.
- Keep resolve/commit semantics unchanged so deterministic behavior survives scaling.

## TODO
- Add shard-transfer refusal codes and migration examples.
- Add cross-shard proof artifact schema once networking is introduced.
- Add shard-health invariants to AuditX strict checks.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/deterministic_parallelism.md`
- `docs/architecture/hash_anchors.md`
- `docs/architecture/session_lifecycle.md`
