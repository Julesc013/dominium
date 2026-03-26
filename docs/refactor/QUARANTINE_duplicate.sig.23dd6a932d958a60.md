Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.23dd6a932d958a60`

- Symbol: `_parser`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/system/tool_run_sys_stress.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/chem/tool_generate_chem_stress.py`
- `tools/chem/tool_replay_chem_window.py`
- `tools/chem/tool_run_chem_stress.py`
- `tools/compat/tool_apply_migration.py`
- `tools/compat/tool_plan_migration.py`
- `tools/compat/tool_replay_migration.py`
- `tools/control/tool_determinism_compare.py`
- `tools/control/tool_global_control_stress.py`
- `tools/control/tool_run_control_stress.py`
- `tools/earth/tool_generate_earth_mvp_stress.py`
- `tools/earth/tool_replay_earth_physics_window.py`
- `tools/earth/tool_replay_earth_view_window.py`
- `tools/earth/tool_run_earth_mvp_stress.py`
- `tools/electric/tool_generate_elec_stress_scenario.py`
- `tools/electric/tool_replay_elec_window.py`
- `tools/electric/tool_run_elec_stress.py`
- `tools/fluid/tool_generate_fluid_stress.py`
- `tools/fluid/tool_replay_fluid_window.py`
- `tools/fluid/tool_run_fluid_stress.py`
- `tools/geo/tool_generate_geo_stress.py`
- `tools/geo/tool_run_geo_stress.py`
- `tools/materials/tool_generate_factory_planet_scenario.py`
- `tools/materials/tool_run_stress.py`
- `tools/mobility/tool_determinism_compare.py`
- `tools/mobility/tool_mobility_stress.py`
- `tools/pollution/tool_generate_poll_stress.py`
- `tools/pollution/tool_run_poll_stress.py`
- `tools/signals/tool_generate_sig_stress_scenario.py`
- `tools/signals/tool_replay_sig_window.py`
- `tools/signals/tool_run_sig_stress.py`
- `tools/system/tool_generate_sys_stress.py`
- `tools/system/tool_run_sys_stress.py`
- `tools/thermal/tool_generate_therm_stress_scenario.py`
- `tools/thermal/tool_replay_therm_window.py`
- `tools/thermal/tool_run_therm_stress.py`

## Scorecard

- `tools/system/tool_run_sys_stress.py` disposition=`canonical` rank=`1` total_score=`81.19` risk=`HIGH`
- `tools/earth/tool_replay_earth_view_window.py` disposition=`quarantine` rank=`2` total_score=`78.09` risk=`HIGH`
- `tools/compat/tool_apply_migration.py` disposition=`quarantine` rank=`3` total_score=`76.07` risk=`HIGH`
- `tools/compat/tool_plan_migration.py` disposition=`quarantine` rank=`4` total_score=`76.07` risk=`HIGH`
- `tools/fluid/tool_generate_fluid_stress.py` disposition=`quarantine` rank=`5` total_score=`75.65` risk=`HIGH`
- `tools/thermal/tool_generate_therm_stress_scenario.py` disposition=`quarantine` rank=`6` total_score=`74.15` risk=`HIGH`
- `tools/chem/tool_run_chem_stress.py` disposition=`quarantine` rank=`7` total_score=`72.38` risk=`HIGH`
- `tools/electric/tool_generate_elec_stress_scenario.py` disposition=`merge` rank=`8` total_score=`71.06` risk=`HIGH`
- `tools/system/tool_generate_sys_stress.py` disposition=`merge` rank=`9` total_score=`71.01` risk=`HIGH`
- `tools/chem/tool_generate_chem_stress.py` disposition=`merge` rank=`10` total_score=`70.62` risk=`HIGH`
- `tools/fluid/tool_run_fluid_stress.py` disposition=`merge` rank=`11` total_score=`69.94` risk=`HIGH`
- `tools/control/tool_run_control_stress.py` disposition=`merge` rank=`12` total_score=`67.86` risk=`HIGH`
- `tools/geo/tool_run_geo_stress.py` disposition=`merge` rank=`13` total_score=`67.55` risk=`HIGH`
- `tools/thermal/tool_run_therm_stress.py` disposition=`merge` rank=`14` total_score=`67.48` risk=`HIGH`
- `tools/compat/tool_replay_migration.py` disposition=`merge` rank=`15` total_score=`67.44` risk=`HIGH`
- `tools/chem/tool_replay_chem_window.py` disposition=`merge` rank=`16` total_score=`67.39` risk=`HIGH`
- `tools/signals/tool_generate_sig_stress_scenario.py` disposition=`merge` rank=`17` total_score=`67.08` risk=`HIGH`
- `tools/earth/tool_run_earth_mvp_stress.py` disposition=`merge` rank=`18` total_score=`66.58` risk=`HIGH`
- `tools/materials/tool_run_stress.py` disposition=`merge` rank=`19` total_score=`66.12` risk=`HIGH`
- `tools/fluid/tool_replay_fluid_window.py` disposition=`merge` rank=`20` total_score=`65.46` risk=`HIGH`
- `tools/earth/tool_generate_earth_mvp_stress.py` disposition=`merge` rank=`21` total_score=`64.65` risk=`HIGH`
- `tools/earth/tool_replay_earth_physics_window.py` disposition=`merge` rank=`22` total_score=`64.65` risk=`HIGH`
- `tools/geo/tool_generate_geo_stress.py` disposition=`merge` rank=`23` total_score=`64.65` risk=`HIGH`
- `tools/electric/tool_run_elec_stress.py` disposition=`merge` rank=`24` total_score=`64.57` risk=`HIGH`
- `tools/thermal/tool_replay_therm_window.py` disposition=`merge` rank=`25` total_score=`64.5` risk=`HIGH`
- `tools/pollution/tool_generate_poll_stress.py` disposition=`merge` rank=`26` total_score=`63.68` risk=`HIGH`
- `tools/signals/tool_run_sig_stress.py` disposition=`merge` rank=`27` total_score=`63.67` risk=`HIGH`
- `tools/signals/tool_replay_sig_window.py` disposition=`merge` rank=`28` total_score=`63.6` risk=`HIGH`
- `tools/mobility/tool_mobility_stress.py` disposition=`merge` rank=`29` total_score=`63.57` risk=`HIGH`
- `tools/electric/tool_replay_elec_window.py` disposition=`merge` rank=`30` total_score=`63.54` risk=`HIGH`
- `tools/mobility/tool_determinism_compare.py` disposition=`merge` rank=`31` total_score=`62.63` risk=`HIGH`
- `tools/pollution/tool_run_poll_stress.py` disposition=`merge` rank=`32` total_score=`61.62` risk=`HIGH`
- `tools/materials/tool_generate_factory_planet_scenario.py` disposition=`merge` rank=`33` total_score=`61.2` risk=`HIGH`
- `tools/control/tool_global_control_stress.py` disposition=`merge` rank=`34` total_score=`60.51` risk=`HIGH`
- `tools/control/tool_determinism_compare.py` disposition=`merge` rank=`35` total_score=`59.18` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/TIME_ANCHOR0_RETRO_AUDIT.md, docs/governance/REPOX_RULESETS.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
