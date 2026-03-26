Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.2351c426b576318f`

- Symbol: `ensure_clean_dir`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/app/app_cli_contracts.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tests/app/app_buildmeta_tests.py`
- `tests/app/app_cli_contracts.py`
- `tests/app/app_ui_contracts.py`
- `tests/app/slice0_flow_tests.py`
- `tests/app/slice1_physical_tests.py`
- `tests/app/slice2_coordination_tests.py`
- `tests/integration/blueprint_refusal_tests.py`
- `tests/integration/capability_runtime_enforcement_tests.py`
- `tests/integration/client_flow_smoke_tests.py`
- `tests/integration/client_parity_tests.py`
- `tests/integration/client_refusal_codes_tests.py`
- `tests/integration/exploration_baseline_tests.py`
- `tests/integration/exploration_scaling_tests.py`
- `tests/integration/freecam_epistemics_tests.py`
- `tests/integration/interaction_baseline_tests.py`
- `tests/integration/interaction_scaling_tests.py`
- `tests/integration/server_discovery_tests.py`
- `tests/integration/server_tools_operational_tests.py`
- `tests/integration/signal_baseline_tests.py`
- `tests/integration/signal_scaling_tests.py`
- `tests/integration/world_manager_tests.py`
- `tests/playtest/playtest_mode_parity_tests.py`
- `tests/playtest/playtest_replay_regression_tests.py`
- `tests/playtest/playtest_scenario_parity_tests.py`
- `tests/playtest/playtest_variant_replay_tests.py`
- `tests/ui_parity/client_menu_parity_tests.py`
- `tests/ux/ux_presentation_tests.py`

## Scorecard

- `tests/app/app_cli_contracts.py` disposition=`canonical` rank=`1` total_score=`83.21` risk=`HIGH`
- `tests/app/app_ui_contracts.py` disposition=`quarantine` rank=`2` total_score=`83.21` risk=`HIGH`
- `tests/integration/client_refusal_codes_tests.py` disposition=`merge` rank=`3` total_score=`69.32` risk=`HIGH`
- `tests/integration/exploration_baseline_tests.py` disposition=`merge` rank=`4` total_score=`66.43` risk=`HIGH`
- `tests/ux/ux_presentation_tests.py` disposition=`merge` rank=`5` total_score=`65.98` risk=`HIGH`
- `tests/integration/interaction_baseline_tests.py` disposition=`merge` rank=`6` total_score=`63.6` risk=`HIGH`
- `tests/integration/signal_baseline_tests.py` disposition=`merge` rank=`7` total_score=`63.6` risk=`HIGH`
- `tests/integration/client_parity_tests.py` disposition=`merge` rank=`8` total_score=`62.63` risk=`HIGH`
- `tests/integration/freecam_epistemics_tests.py` disposition=`merge` rank=`9` total_score=`61.67` risk=`HIGH`
- `tests/playtest/playtest_scenario_parity_tests.py` disposition=`merge` rank=`10` total_score=`61.67` risk=`HIGH`
- `tests/integration/blueprint_refusal_tests.py` disposition=`merge` rank=`11` total_score=`61.21` risk=`HIGH`
- `tests/integration/capability_runtime_enforcement_tests.py` disposition=`merge` rank=`12` total_score=`61.21` risk=`HIGH`
- `tests/integration/client_flow_smoke_tests.py` disposition=`merge` rank=`13` total_score=`61.21` risk=`HIGH`
- `tests/integration/interaction_scaling_tests.py` disposition=`merge` rank=`14` total_score=`60.25` risk=`HIGH`
- `tests/integration/server_discovery_tests.py` disposition=`merge` rank=`15` total_score=`60.25` risk=`HIGH`
- `tests/integration/signal_scaling_tests.py` disposition=`merge` rank=`16` total_score=`60.25` risk=`HIGH`
- `tests/ui_parity/client_menu_parity_tests.py` disposition=`merge` rank=`17` total_score=`60.25` risk=`HIGH`
- `tests/playtest/playtest_mode_parity_tests.py` disposition=`merge` rank=`18` total_score=`59.64` risk=`HIGH`
- `tests/integration/exploration_scaling_tests.py` disposition=`merge` rank=`19` total_score=`59.29` risk=`HIGH`
- `tests/integration/world_manager_tests.py` disposition=`merge` rank=`20` total_score=`59.29` risk=`HIGH`
- `tests/playtest/playtest_replay_regression_tests.py` disposition=`merge` rank=`21` total_score=`59.29` risk=`HIGH`
- `tests/integration/server_tools_operational_tests.py` disposition=`merge` rank=`22` total_score=`57.27` risk=`HIGH`
- `tests/playtest/playtest_variant_replay_tests.py` disposition=`merge` rank=`23` total_score=`53.69` risk=`HIGH`
- `tests/app/app_buildmeta_tests.py` disposition=`drop` rank=`24` total_score=`53.33` risk=`HIGH`
- `tests/app/slice0_flow_tests.py` disposition=`merge` rank=`25` total_score=`52.14` risk=`HIGH`
- `tests/app/slice1_physical_tests.py` disposition=`merge` rank=`26` total_score=`52.14` risk=`HIGH`
- `tests/app/slice2_coordination_tests.py` disposition=`merge` rank=`27` total_score=`52.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/README.md, docs/app/TESTX_COMPLIANCE.md, docs/app/TESTX_INVENTORY.md, docs/appshell/APPSHELL_CONSTITUTION.md, docs/appshell/COMMANDS_AND_REFUSALS.md, docs/appshell/IPC_ATTACH_CONSOLES.md, docs/appshell/SUPERVISOR_MODEL.md, docs/appshell/TUI_FRAMEWORK.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
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
