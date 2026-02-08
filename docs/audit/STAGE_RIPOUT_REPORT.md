Status: DERIVED
Purpose: Stage-gating token removal and capability-gating reconciliation report
Authority: NON-CANONICAL

Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Stage Ripout Report

## Scope

- Remove stage-gating identifiers from runtime/schema/test/tool surfaces.
- Keep documentation references as planning-only language.
- Preserve behavior with capability-based gating only.

## Deterministic Mapping Used

- `stage_0_nonbio` -> `capset_world_nonbio`
- `stage_1_nonintelligent_life` -> `capset_world_life_nonintelligent`
- `stage_2_intelligent_pre_tool` -> `capset_world_life_intelligent`
- `stage_3_pre_tool_world` -> `capset_world_pretool`
- `stage_4_pre_industry` -> `capset_society_institutions`
- `stage_5_pre_present` -> `capset_infrastructure_industry`
- `stage_6_future` -> `capset_future_affordances`
- `world_stage.json` -> `world_capabilities.json`

## Files Updated in This Pass

- `tests/fixtures/worlds/capset_world_nonbio/world_capabilities.json` (renamed)
- `tests/fixtures/worlds/capset_world_life_nonintelligent/world_capabilities.json` (renamed)
- `tests/fixtures/worlds/capset_world_life_intelligent/world_capabilities.json` (renamed)
- `tests/fixtures/worlds/capset_world_pretool/world_capabilities.json` (renamed)
- `tests/fixtures/worlds/capset_society_institutions/world_capabilities.json` (renamed)
- `tests/fixtures/worlds/capset_infrastructure_industry/world_capabilities.json` (renamed)
- `tests/fixtures/worlds/capset_future_affordances/world_capabilities.json` (renamed)
- `tests/testx/capability_sets/*` (renamed from stage directories)
- `tests/testx/capability_regression/*` (renamed from stage_regression)
- `tests/testx/CAPABILITY_MATRIX.yaml`
- `tests/testx/capability_matrix_contracts.py`
- `tests/contract/CMakeLists.txt`
- `tests/contract/capability_gating_contracts.py`
- `scripts/ci/check_repox_rules.py`
- `scripts/audit/generate_inventory.py`

## Verification Commands

- `rg -n "STAGE_|requires_stage|provides_stage|stage_features|required_stage" engine game client server setup launcher tools libs schema tests`
- `python scripts/ci/check_repox_rules.py --repo-root .`
- `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game`
- `cmake --build out/build/vs2026/verify --config Debug --target testx_all`

## Verification Result

- Stage-gating token scan outside documentation: PASS (no matches).
- RepoX governance rules: PASS.
- Strict engine/game build: PASS.
- Full TestX gate (`testx_all`): PASS.

## Invariant Confirmation

- Capability-only gating invariant holds for runtime/schema/tests/tools in this pass.
- No simulation semantics were changed.
