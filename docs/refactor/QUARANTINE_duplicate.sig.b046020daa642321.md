Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b046020daa642321`

- Symbol: `_fingerprint`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/pack_compat1_testlib.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/appshell/command_registry.py`
- `src/appshell/diag/diag_snapshot.py`
- `src/appshell/ipc/ipc_transport.py`
- `src/appshell/logging/log_engine.py`
- `src/appshell/paths/virtual_paths.py`
- `src/appshell/tui/tui_engine.py`
- `src/diag/repro_bundle_builder.py`
- `src/lib/install/install_discovery_engine.py`
- `src/packs/compat/pack_compat_validator.py`
- `src/packs/compat/pack_verification_pipeline.py`
- `src/ui/ui_model.py`
- `tools/mvp/toolchain_matrix_common.py`
- `tools/xstack/testx/tests/pack_compat1_testlib.py`

## Scorecard

- `tools/xstack/testx/tests/pack_compat1_testlib.py` disposition=`canonical` rank=`1` total_score=`79.55` risk=`HIGH`
- `tools/mvp/toolchain_matrix_common.py` disposition=`quarantine` rank=`2` total_score=`77.85` risk=`HIGH`
- `src/appshell/command_registry.py` disposition=`quarantine` rank=`3` total_score=`76.55` risk=`HIGH`
- `src/appshell/paths/virtual_paths.py` disposition=`quarantine` rank=`4` total_score=`73.87` risk=`HIGH`
- `src/lib/install/install_discovery_engine.py` disposition=`quarantine` rank=`5` total_score=`73.09` risk=`HIGH`
- `src/appshell/diag/diag_snapshot.py` disposition=`merge` rank=`6` total_score=`69.46` risk=`HIGH`
- `src/appshell/logging/log_engine.py` disposition=`merge` rank=`7` total_score=`69.46` risk=`HIGH`
- `src/ui/ui_model.py` disposition=`merge` rank=`8` total_score=`68.57` risk=`HIGH`
- `src/appshell/tui/tui_engine.py` disposition=`merge` rank=`9` total_score=`66.19` risk=`HIGH`
- `src/appshell/ipc/ipc_transport.py` disposition=`merge` rank=`10` total_score=`64.11` risk=`HIGH`
- `src/diag/repro_bundle_builder.py` disposition=`merge` rank=`11` total_score=`62.86` risk=`HIGH`
- `src/packs/compat/pack_verification_pipeline.py` disposition=`merge` rank=`12` total_score=`59.17` risk=`HIGH`
- `src/packs/compat/pack_compat_validator.py` disposition=`merge` rank=`13` total_score=`57.38` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/VALIDATION_STACK_MAP.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
