Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `data/registries/semantic_contract_registry.json`, and `schema/universe/universe_contract_bundle.schema`.
Stability: stable
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Semantic Contract Model

## Purpose
- Semantic contracts version behavior meaning, not payload shape.
- They prevent silent reinterpretation of replay-critical rules.
- They keep old universes pinned to the meaning they were created under.

## Scope
Semantic contracts govern the meaning of:
- worldgen refinement behavior
- overlay merge resolution
- logic evaluation semantics
- process capsule validity rules
- system collapse and expand rules
- GEO metric behavior
- GEO projection behavior
- GEO partition behavior
- app shell lifecycle semantics

Schemas version structure.
Semantic contracts version meaning.

## Registry
- Source of truth: `data/registries/semantic_contract_registry.json`
- Initial baseline is the `v1` family:
  - `contract.worldgen.refinement.v1`
  - `contract.overlay.merge.v1`
  - `contract.logic.eval.v1`
  - `contract.proc.capsule.v1`
  - `contract.sys.collapse.v1`
  - `contract.geo.metric.v1`
  - `contract.geo.projection.v1`
  - `contract.geo.partition.v1`
  - `contract.appshell.lifecycle.v1`

Each registry row declares:
- `contract_id`
- `version`
- `description`
- `guaranteed_invariants`
- `allowed_evolution`
- `breaking_change_requires`
- `deterministic_fingerprint`

## Universe Binding
- Universe creation writes an immutable sidecar: `universe_contract_bundle.json`.
- The sidecar is validated by `schemas/universe_contract_bundle.schema.json`.
- `UniverseIdentity` stores `universe_contract_bundle_ref` and `universe_contract_bundle_hash`.
- `SessionSpec` stores `contract_bundle_hash` and may also store `semantic_contract_registry_hash`.
- The sidecar is kept out of `UniverseIdentity.identity_hash` on purpose so existing object-id derivation does not drift.
- This is an explicit compatibility-preserving split between identity hashing and semantic pin metadata.

The sidecar pins:
- `contract_worldgen_refinement_version`
- `contract_overlay_merge_version`
- `contract_logic_eval_version`
- `contract_proc_capsule_version`
- `contract_sys_collapse_version`
- `contract_geo_metric_version`
- `contract_geo_projection_version`
- `contract_geo_partition_version`
- `contract_appshell_lifecycle_version`

## Replay And Proof
- Proof surfaces must carry:
  - semantic contract registry hash
  - universe contract bundle hash
- Load refuses `refusal.contract.missing_bundle` when a universe/session artifact does not carry the required contract pins.
- Load and replay refuse `refusal.contract.mismatch` when pinned contract hashes do not match runtime expectations.
- Replay must compare the pinned bundle against the replay bundle.
- If contract versions differ, replay refuses unless an explicit CompatX migration tool is invoked.

## Evolution Rules
- Any semantic meaning change requires a new contract entry.
- Existing universes remain pinned to their original contract bundle.
- Silent semantic drift is forbidden.

Breaking semantic changes require all of:
- a new versioned contract entry
- CompatX migration descriptor
- explicit migration tool or explicit refusal path
- regression lock update
- release notes

## Non-Goals
- No runtime behavior change is authorized by this document.
- No schema-shape change is implied by a semantic contract bump.
- No migration is automatic.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`
- `docs/governance/COMPATX_MODEL.md`
- `docs/universe/UNIVERSE_IDENTITY_STATE.md`
- `data/registries/semantic_contract_registry.json`
- `schema/universe/universe_contract_bundle.schema`
