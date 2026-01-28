# Contracts Index (CONST0)

Status: binding.
Scope: index of frozen and evolving constitutional surfaces.

This index is the navigation hub for stability surfaces. "FROZEN" means the
document defines a contract that must not change lightly. "EVOLVING" means the
document is binding but still expected to grow or sharpen.

## Frozen constitutional surfaces
| Contract | Stability | Notes |
| --- | --- | --- |
| `docs/architecture/ARCH0_CONSTITUTION.md` | FROZEN | Top-level architecture law |
| `docs/architecture/INVARIANTS.md` | FROZEN | Canonical invariant registry |
| `docs/architecture/CANONICAL_SYSTEM_MAP.md` | FROZEN | Dependency direction and forbidden edges |
| `docs/architecture/REPO_NAV.md` | FROZEN | Where work belongs in the repo |
| `docs/architecture/ID_AND_NAMESPACE_RULES.md` | FROZEN | ID shape, stability, and reservations |
| `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md` | FROZEN | Global ordering rules |
| `docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md` | FROZEN | Mechanism vs meaning boundary |
| `docs/architecture/PROCESS_ONLY_MUTATION.md` | FROZEN | Only lawful state mutation path |
| `docs/architecture/LAW_AND_META_LAW.md` | FROZEN | Historical law vs operational law |
| `docs/architecture/REFUSAL_SEMANTICS.md` | FROZEN | Canonical refusal codes and payload |
| `docs/architecture/UNIT_SYSTEM_POLICY.md` | FROZEN | Units, fixed-point, and numeric policy |
| `docs/architecture/FABRICATION_MODEL.md` | FROZEN | Fabrication ontology and schema rules |
| `docs/architecture/EXECUTION_MODEL.md` | FROZEN | Work IR and deterministic execution |
| `docs/architecture/EXECUTION_REORDERING_POLICY.md` | FROZEN | Canonical commit ordering |
| `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md` | FROZEN | Deterministic reduction operators |
| `docs/architecture/LAW_ENFORCEMENT_POINTS.md` | FROZEN | Mandatory law gates |
| `docs/architecture/GLOBAL_ID_MODEL.md` | FROZEN | Deterministic global ID rules |
| `docs/architecture/CROSS_SHARD_LOG.md` | FROZEN | Cross-shard ordering and idempotence |
| `docs/architecture/BUDGET_POLICY.md` | FROZEN | Budget admission and refusal mapping |
| `docs/architecture/PERFORMANCE_METRICS.md` | FROZEN | Derived metrics for PERF fixtures |
| `docs/architecture/CODE_DATA_BOUNDARY.md` | FROZEN | Code vs data ownership rules |
| `docs/architecture/SEMANTIC_STABILITY_POLICY.md` | FROZEN | No reuse and no silent reinterpretation |
| `docs/architecture/ANTI_ENTROPY_RULES.md` | FROZEN | Anti-entropy requirements |
| `docs/architecture/CAPABILITY_BASELINES.md` | FROZEN | Capability baselines and refusals |
| `docs/distribution/PACK_TAXONOMY.md` | FROZEN | Canonical pack classes |
| `docs/distribution/LAUNCHER_SETUP_CONTRACT.md` | FROZEN | Distribution and launcher/setup rules |
| `docs/distribution/LEGACY_COMPATIBILITY.md` | FROZEN | Legacy compatibility modes |

## Evolving but binding surfaces
| Contract | Stability | Notes |
| --- | --- | --- |
| `docs/architecture/ARCH_REPO_LAYOUT.md` | EVOLVING | Layout is binding but may refine |
| `docs/architecture/DIRECTORY_STRUCTURE.md` | EVOLVING | Canonical tree and runtime root |
| `docs/architecture/MACRO_TIME_MODEL.md` | EVOLVING | Macro stepping rules |
| `docs/architecture/DISTRIBUTED_SIM_MODEL.md` | EVOLVING | Distributed simulation details |
| `docs/architecture/DISTRIBUTED_TIME_MODEL.md` | EVOLVING | Distributed time details |
| `docs/architecture/JOIN_RESYNC_CONTRACT.md` | EVOLVING | Join and resync rules |
| `docs/architecture/SHARD_LIFECYCLE.md` | EVOLVING | Shard lifecycle rules |
| `docs/architecture/CHECKPOINTING_MODEL.md` | EVOLVING | Checkpointing and snapshots |
| `docs/architecture/CRASH_RECOVERY.md` | EVOLVING | Recovery contracts |
| `docs/architecture/ROLLING_UPDATES.md` | EVOLVING | Rolling update contracts |
| `docs/architecture/PERFORMANCE_PROOF.md` | EVOLVING | PERF stress evidence and regression proof |
| `docs/engine/FAB_INTERPRETERS.md` | EVOLVING | Minimal FAB interpreter contract |
| `docs/game/FAB_EXECUTION_FLOW.md` | EVOLVING | FAB execution flow and guardrails |

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
- `schema/profile.schema`

Refusal code anchors:
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `schema/integrity/SPEC_REFUSAL_CODES.md`

Ordering anchors:
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/EXECUTION_REORDERING_POLICY.md`
- `docs/architecture/CROSS_SHARD_LOG.md`

## Enforcement
Contract enforcement lives under:
- `tests/contract/`
- `tests/app/` (legacy and adjacent contract checks)
