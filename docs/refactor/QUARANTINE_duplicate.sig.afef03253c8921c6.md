Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.afef03253c8921c6`

- Symbol: `stat`
- Cluster Kind: `exact`
- Cluster Resolution: `merge`
- Risk Level: `MED`
- Canonical Candidate: `game/tests/tests/setup/test_adapter_macos_gui.cpp`
- Quarantine Reasons: `builtin_or_entrypoint_collision, cross_domain_helper_collision, file_scope_ambiguity, phase_boundary_deferred, requires_medium_risk_batch_gate, requires_single_action_full_gate, test_runtime_split`
- Planned Action Kinds: `merge, rewire, deprecate`

## Competing Files

- `engine/modules/system/dsys_dir_sorted.c`
- `game/tests/tests/setup/conformance/setup_conformance_repeat_tests.cpp`
- `game/tests/tests/setup/conformance/setup_conformance_runner.cpp`
- `game/tests/tests/setup/gold_master/setup_gold_master_tests.cpp`
- `game/tests/tests/setup/parity_lock/setup_parity_lock_tests.cpp`
- `game/tests/tests/setup/test_adapter_macos_gui.cpp`
- `game/tests/tests/setup/test_apply.cpp`
- `game/tests/tests/setup/test_cli_golden.cpp`
- `launcher/cli/launcher_ui_shell.c`
- `tools/ui_preview_host/common/ui_preview_common.cpp`
- `tools/validation/validator_common.cpp`

## Scorecard

- `game/tests/tests/setup/test_adapter_macos_gui.cpp` disposition=`canonical` rank=`1` total_score=`61.43` risk=`MED`
- `tools/validation/validator_common.cpp` disposition=`drop` rank=`2` total_score=`60.73` risk=`HIGH`
- `engine/modules/system/dsys_dir_sorted.c` disposition=`merge` rank=`3` total_score=`58.75` risk=`MED`
- `tools/ui_preview_host/common/ui_preview_common.cpp` disposition=`drop` rank=`4` total_score=`57.51` risk=`LOW`
- `game/tests/tests/setup/conformance/setup_conformance_repeat_tests.cpp` disposition=`drop` rank=`5` total_score=`57.38` risk=`MED`
- `game/tests/tests/setup/test_cli_golden.cpp` disposition=`merge` rank=`6` total_score=`57.38` risk=`MED`
- `launcher/cli/launcher_ui_shell.c` disposition=`merge` rank=`7` total_score=`54.54` risk=`MED`
- `game/tests/tests/setup/parity_lock/setup_parity_lock_tests.cpp` disposition=`drop` rank=`8` total_score=`54.17` risk=`MED`
- `game/tests/tests/setup/conformance/setup_conformance_runner.cpp` disposition=`drop` rank=`9` total_score=`53.57` risk=`MED`
- `game/tests/tests/setup/gold_master/setup_gold_master_tests.cpp` disposition=`drop` rank=`10` total_score=`53.57` risk=`MED`
- `game/tests/tests/setup/test_apply.cpp` disposition=`merge` rank=`11` total_score=`53.57` risk=`MED`

## Usage Sites

- Build Targets: `setup_adapter_macos_gui_tests`
- Docs: `none`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
