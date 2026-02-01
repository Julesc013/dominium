Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Schema Stability (CLEAN1)

Status: binding.
Scope: project-level freeze status for schema contracts.

This document classifies schemas as FROZEN or EVOLVING.
Schema metadata is still authoritative for versioning; see:

- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_MIGRATION.md`
- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`

## Rules

- FROZEN schemas MUST NOT change meaning without explicit migration or refusal.
- EVOLVING schemas may add fields using skip-unknown compatibility only.
- All schemas must carry schema_id, schema_version, and stability fields.
- Unknown fields must round-trip unchanged.

## Stability table

| Schema | Stability | Notes |
| --- | --- | --- |
| `schema/authority.schema` | FROZEN | Authority contract surface |
| `schema/capability.schema` | FROZEN | Capability identity and semantics |
| `schema/capability_baseline.schema` | FROZEN | Baseline capabilities |
| `schema/capability_lockfile.schema` | FROZEN | Deterministic pack locking |
| `schema/pack_manifest.schema` | FROZEN | Pack format and identity |
| `schema/world_definition.schema` | FROZEN | World template contract |
| `schema/process.schema` | FROZEN | Process execution contract |
| `schema/save_and_replay.schema` | FROZEN | Save/replay persistence contract |
| `schema/server_protocol.schema` | FROZEN | Network protocol contract |
| `schema/domain.schema` | FROZEN | Domain identity and bounds |
| `schema/field.schema` | FROZEN | Field identity and typing |
| `schema/topology.schema` | FROZEN | Topology structure contract |
| `schema/snapshot.schema` | FROZEN | Snapshot serialization |
| `schema/checkpoint.schema` | FROZEN | Checkpoint serialization |
| `schema/shard_lifecycle.schema` | FROZEN | Shard lifecycle contract |
| `schema/macro_capsule.schema` | FROZEN | Macro capsule contract |
| `schema/macro_schedule.schema` | FROZEN | Macro scheduling contract |
| `schema/macro_event_queue.schema` | FROZEN | Macro event queue contract |
| `schema/cross_shard_message.schema` | FROZEN | Cross-shard message format |
| `schema/budget_policy.schema` | FROZEN | Budget policy contract |
| `schema/budget_snapshot.schema` | FROZEN | Budget telemetry format |
| `schema/refinement_plan.schema` | FROZEN | Refinement plan contract |
| `schema/network.schema` | FROZEN | Network intent format |
| `schema/measurement_artifact.schema` | FROZEN | Measurement artifact format |
| `schema/material.schema` | FROZEN | FAB material model |
| `schema/substance.schema` | FROZEN | FAB substance model |
| `schema/interface.schema` | FROZEN | FAB interface model |
| `schema/part.schema` | FROZEN | FAB part model |
| `schema/assembly.schema` | FROZEN | FAB assembly model |
| `schema/process_family.schema` | FROZEN | FAB process families |
| `schema/instrument.schema` | FROZEN | FAB instruments |
| `schema/standard.schema` | FROZEN | FAB standards |
| `schema/quality.schema` | FROZEN | FAB quality model |
| `schema/batch_lot.schema` | FROZEN | Batch and provenance |
| `schema/profile.schema` | FROZEN | Distribution profile data |
| `schema/worldgen_model.schema` | EVOLVING | Worldgen anchors and fields |
| `schema/institution.schema` | EVOLVING | Institution and governance data |
| `schema/knowledge.schema` | EVOLVING | Knowledge artifacts |
| `schema/part_and_interface.schema` | EVOLVING | Transitional helper schema |
| `schema/accessibility_preset.schema` | EVOLVING | Presentation presets |
| `schema/hud_layout.schema` | EVOLVING | HUD composition |
| `schema/localization_pack.schema` | EVOLVING | Localization packs |

## Migration requirements

- MAJOR schema bumps require migration notes in `schema/SCHEMA_MIGRATION.md`.
- FROZEN schema changes require an explicit change log entry and updated hash in
  `docs/architecture/FROZEN_CONTRACT_HASHES.json`.