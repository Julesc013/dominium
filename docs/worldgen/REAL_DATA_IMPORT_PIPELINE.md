Status: CANONICAL
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0, `docs/canon/glossary_v1.md` v1.0.0, and `AGENTS.md`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Real Data Import Pipeline

## Purpose
Define deterministic integration of external astronomy and terrain datasets through pack-driven source ingestion and derived artifact generation.

## Source Pack vs Derived Pack
1. Source Pack
- Contains raw licensed source artifacts and source metadata.
- May include large files and provider-native formats.
- Is not required in distribution output by default.

2. Derived Pack
- Contains deterministic converted artifacts consumed by runtime tooling.
- Must be reproducible from declared source inputs and generator tool versions.
- Must include provenance headers for every canonical derived artifact.

## Deterministic Import Rules
1. Import tools must consume source files in deterministic lexical order.
2. Import tools must use explicit sampling intervals and fixed numeric precision.
3. Import tools must canonical-serialize JSON outputs before hashing.
4. Import tools must not use wall clock values as canonical inputs.
5. Any nondeterministic run metadata must be excluded from canonical hashes.

## Provenance Header Contract
All derived artifacts must include a `provenance` object with:
- `artifact_type_id`
- `source_pack_id`
- `source_hash`
- `generator_tool_id`
- `generator_tool_version`
- `schema_version`
- `input_merkle_hash`
- `pack_lock_hash`
- `deterministic`

`deterministic` must be `true` for canonical artifacts.

## Regeneration Discipline
1. Source hash unchanged + generator unchanged + schema unchanged => identical derived hash.
2. Source change => derived hash must change deterministically.
3. Generator version change requires explicit regeneration and updated provenance.
4. Hand-editing derived artifacts is forbidden; regeneration must occur through import tools.

## Floating-Point Determinism Strategy
1. Import stage may parse provider floating-point values.
2. Canonical outputs must normalize numeric precision explicitly:
- fixed decimal rounding for continuous values
- integer millimeter or fixed-point fields where possible
3. Do not preserve source provider binary float noise in canonical outputs.

## Precision Policy
1. Ingestion accepts provider double precision values.
2. Derived canonical artifacts normalize to deterministic decimal/fixed-point form.
3. Runtime-facing structures consume normalized values only.

## Universe Index Integration
1. Derived ephemeris tables feed deterministic object-position lookup channels.
2. Derived terrain tile pyramids feed deterministic ROI tile selection.
3. UniverseIndex references derived packs only; source packs are not read at runtime.

## Macro/Micro Consistency
1. Macro capsule parameters derive from canonical bounds and body parameters.
2. Micro refinement selects derived terrain tiles by deterministic ROI ordering.
3. Expand/collapse continues to use process-only mutation and conservation checks.

## Refusal Codes
- `refusal.data_source_missing`
- `refusal.data_schema_invalid`
- `refusal.data_import_failed`
- `refusal.provenance_missing`
- `refusal.constraints_unsatisfiable` (search stage)
- `refusal.search_exhausted` (search stage)

## Cross-References
- `docs/worldgen/WORLDGEN_PIPELINE.md`
- `docs/worldgen/WORLDGEN_CONSTRAINTS.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/interest_regions.md`
- `docs/architecture/macro_capsules.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/contracts/refusal_contract.md`
