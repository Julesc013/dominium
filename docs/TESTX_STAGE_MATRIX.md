Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# TESTX_STAGE_MATRIX

Machine-readable source of truth:
- `tests/testx/STAGE_MATRIX.yaml`

Required stages:
- `STAGE_0_NONBIO_WORLD`
- `STAGE_1_NONINTELLIGENT_LIFE`
- `STAGE_2_INTELLIGENT_PRE_TOOL`
- `STAGE_3_PRE_TOOL_WORLD`
- `STAGE_4_PRE_INDUSTRY`
- `STAGE_5_PRE_PRESENT`
- `STAGE_6_FUTURE`

Required per-stage suites (all stages):
- `test_load_and_validate`
- `test_command_surface`
- `test_pack_gating`
- `test_epistemics`
- `test_determinism_smoke`
- `test_replay_hash`

Per-stage fixtures:
- `tests/fixtures/worlds/stage_0_nonbio/world_stage.json`
- `tests/fixtures/worlds/stage_1_nonintelligent_life/world_stage.json`
- `tests/fixtures/worlds/stage_2_intelligent_pre_tool/world_stage.json`
- `tests/fixtures/worlds/stage_3_pre_tool_world/world_stage.json`
- `tests/fixtures/worlds/stage_4_pre_industry/world_stage.json`
- `tests/fixtures/worlds/stage_5_pre_present/world_stage.json`
- `tests/fixtures/worlds/stage_6_future/world_stage.json`

Anti-creep regression tests:
- `tests/testx/stage_regression/test_no_life_in_stage_0.py`
- `tests/testx/stage_regression/test_no_tools_in_stage_2_and_3.py`
- `tests/testx/stage_regression/test_no_industry_in_stage_4.py`
- `tests/testx/stage_regression/test_no_future_affordances_pre_6.py`

Expected command family progression:
- Stage 0 enabled: none
- Stage 1 enabled: `life`
- Stage 2 enabled: `life`, `tooling`
- Stage 3 enabled: `life`, `tooling`
- Stage 4 enabled: `life`, `tooling`, `institutions`
- Stage 5 enabled: `life`, `tooling`, `institutions`, `industry`
- Stage 6 enabled: `life`, `tooling`, `institutions`, `industry`, `future`

Pack gating contract:
- Accept: `pack.requires_stage <= world.provides_stage`
- Refuse: `pack.requires_stage > world.provides_stage` with `REFUSE_CAPABILITY_STAGE_TOO_LOW`

Determinism and epistemics contract:
- Each suite emits structured failures with stage, fixture, command/pack, and expected vs actual values.
- Command surface and replay hash checks must be deterministic across repeated runs.
- Epistemic scope checks enforce no omniscient disclosure in non-tools command contexts.

CI/TestX wiring:
- Matrix validation test: `stage_matrix_contracts`
- Per-stage suites: `stage_matrix_<stage_dir>_<suite>`
- Anti-creep tests: `stage_regression_*`
- RepoX invariant: `INV-STAGE-MATRIX`

