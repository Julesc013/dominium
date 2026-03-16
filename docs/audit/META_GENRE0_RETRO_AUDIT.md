Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META-GENRE0 Retro-Consistency Audit

Status: AUDIT  
Last Updated: 2026-03-07  
Scope: Player Demand Coverage Matrix (PDCM) constitution and XStack linkage.

## Audit Findings

### 1) RWAM remains the physics-reality axis

Observed:

- `data/meta/real_world_affordance_matrix.json` already defines canonical affordance categories and series coverage.
- Existing series coverage checks (`test_no_series_without_affordance_mapping`) already treat RWAM as the mandatory substrate axis.

Assessment:

- PDCM should reference RWAM affordance IDs directly, not duplicate affordance definitions.

### 2) Existing planning artifacts are fragmented

Observed:

- No single canonical player-demand matrix existed before this work.
- Planning intent is distributed across architecture docs, prompt-series audit docs, and registry contracts.

Assessment:

- A unified machine-readable demand matrix is required to prevent planning drift.

### 3) No conflicting demand matrix detected

Observed:

- No existing `player_demand_matrix` registry or equivalent canonical JSON matrix file was present.
- No existing RepoX invariant enforced feature-to-demand linkage.

Assessment:

- Introducing PDCM as a new canonical artifact does not collide with existing matrix definitions.

### 4) Cross-reference set required for consistency

PDCM must be cross-referenced with:

- `data/meta/real_world_affordance_matrix.json` (RWAM affordances)
- `data/registries/action_family_registry.json` (Action Grammar family IDs)
- `data/registries/action_template_registry.json` (action template IDs)
- `data/registries/explain_contract_registry.json` (explain contract IDs)
- `data/registries/law_profiles.json` + `data/registries/physics_profile_registry.json` (profile knobs)

## Migration Notes

1. Add canonical matrix registry:
   - `data/meta/player_demand_matrix.json`
2. Add human-readable matrix:
   - `docs/meta/PLAYER_DEMAND_COVERAGE_MATRIX.md`
3. Add schema contract:
   - `schema/meta/player_demand_matrix.schema`
4. Add enforcement:
   - RepoX invariant `INV-CHANGE-MUST-REFERENCE-DEMAND`
   - AuditX analyzer `OrphanFeatureSmell`
5. Add validation and gap tooling:
   - TestX matrix tests
   - `tools/meta/tool_generate_demand_gap_report`
