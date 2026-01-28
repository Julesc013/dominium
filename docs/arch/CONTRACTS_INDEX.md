# Contracts Index (CONST0)

Status: binding.
Scope: index of frozen and evolving constitutional surfaces.

This index is the navigation hub for stability surfaces. "FROZEN" means the
document defines a contract that must not change lightly. "EVOLVING" means the
document is binding but still expected to grow or sharpen.

## Frozen constitutional surfaces
| Contract | Stability | Notes |
| --- | --- | --- |
| `docs/arch/ARCH0_CONSTITUTION.md` | FROZEN | Top-level architecture law |
| `docs/arch/INVARIANTS.md` | FROZEN | Canonical invariant registry |
| `docs/arch/CANONICAL_SYSTEM_MAP.md` | FROZEN | Dependency direction and forbidden edges |
| `docs/arch/REPO_NAV.md` | FROZEN | Where work belongs in the repo |
| `docs/arch/ID_AND_NAMESPACE_RULES.md` | FROZEN | ID shape, stability, and reservations |
| `docs/arch/DETERMINISTIC_ORDERING_POLICY.md` | FROZEN | Global ordering rules |
| `docs/arch/CODE_KNOWLEDGE_BOUNDARY.md` | FROZEN | Mechanism vs meaning boundary |
| `docs/arch/PROCESS_ONLY_MUTATION.md` | FROZEN | Only lawful state mutation path |
| `docs/arch/LAW_AND_META_LAW.md` | FROZEN | Historical law vs operational law |
| `docs/arch/REFUSAL_SEMANTICS.md` | FROZEN | Canonical refusal codes and payload |
| `docs/arch/UNIT_SYSTEM_POLICY.md` | FROZEN | Units, fixed-point, and numeric policy |
| `docs/arch/FABRICATION_MODEL.md` | FROZEN | Fabrication ontology and schema rules |
| `docs/arch/EXECUTION_MODEL.md` | FROZEN | Work IR and deterministic execution |
| `docs/arch/EXECUTION_REORDERING_POLICY.md` | FROZEN | Canonical commit ordering |
| `docs/arch/DETERMINISTIC_REDUCTION_RULES.md` | FROZEN | Deterministic reduction operators |
| `docs/arch/LAW_ENFORCEMENT_POINTS.md` | FROZEN | Mandatory law gates |
| `docs/arch/GLOBAL_ID_MODEL.md` | FROZEN | Deterministic global ID rules |
| `docs/arch/CROSS_SHARD_LOG.md` | FROZEN | Cross-shard ordering and idempotence |
| `docs/arch/BUDGET_POLICY.md` | FROZEN | Budget admission and refusal mapping |
| `docs/arch/CODE_DATA_BOUNDARY.md` | FROZEN | Code vs data ownership rules |
| `docs/arch/SEMANTIC_STABILITY_POLICY.md` | FROZEN | No reuse and no silent reinterpretation |
| `docs/arch/ANTI_ENTROPY_RULES.md` | FROZEN | Anti-entropy requirements |
| `docs/arch/CAPABILITY_BASELINES.md` | FROZEN | Capability baselines and refusals |

## Evolving but binding surfaces
| Contract | Stability | Notes |
| --- | --- | --- |
| `docs/arch/ARCH_REPO_LAYOUT.md` | EVOLVING | Layout is binding but may refine |
| `docs/arch/DIRECTORY_STRUCTURE.md` | EVOLVING | Canonical tree and runtime root |
| `docs/arch/MACRO_TIME_MODEL.md` | EVOLVING | Macro stepping rules |
| `docs/arch/DISTRIBUTED_SIM_MODEL.md` | EVOLVING | Distributed simulation details |
| `docs/arch/DISTRIBUTED_TIME_MODEL.md` | EVOLVING | Distributed time details |
| `docs/arch/JOIN_RESYNC_CONTRACT.md` | EVOLVING | Join and resync rules |
| `docs/arch/SHARD_LIFECYCLE.md` | EVOLVING | Shard lifecycle rules |
| `docs/arch/CHECKPOINTING_MODEL.md` | EVOLVING | Checkpointing and snapshots |
| `docs/arch/CRASH_RECOVERY.md` | EVOLVING | Recovery contracts |
| `docs/arch/ROLLING_UPDATES.md` | EVOLVING | Rolling update contracts |

## Schema and contract anchors
Schemas are the authoritative data-shape contracts. Start here:
- `schema/SCHEMA_GOVERNANCE.md`
- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_VALIDATION.md`
- `schema/world_definition.schema`
- `schema/process.schema`
- `schema/save_and_replay.schema`
- `schema/server_protocol.schema`
 - `schema/material.schema`
 - `schema/part.schema`
 - `schema/assembly.schema`
 - `schema/interface.schema`
 - `schema/process_family.schema`
 - `schema/instrument.schema`
 - `schema/standard.schema`
 - `schema/quality.schema`
 - `schema/batch_lot.schema`
 - `schema/hazard.schema`
 - `schema/substance.schema`

Refusal code anchors:
- `docs/arch/REFUSAL_SEMANTICS.md`
- `schema/integrity/SPEC_REFUSAL_CODES.md`

Ordering anchors:
- `docs/arch/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/arch/EXECUTION_REORDERING_POLICY.md`
- `docs/arch/CROSS_SHARD_LOG.md`

## Enforcement
Contract enforcement lives under:
- `tests/contract/`
- `tests/app/` (legacy and adjacent contract checks)
