Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.510a9282eec1421c`

- Symbol: `_write_canonical_json`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/worldgen/worldgen_lock_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/release/release_manifest_engine.py`
- `src/time/epoch_anchor_engine.py`
- `src/validation/validation_engine.py`
- `tools/audit/arch_audit_common.py`
- `tools/data/tool_spice_import.py`
- `tools/data/tool_srtm_import.py`
- `tools/mvp/baseline_universe_common.py`
- `tools/mvp/cross_platform_gate_common.py`
- `tools/mvp/disaster_suite_common.py`
- `tools/mvp/ecosystem_verify_common.py`
- `tools/mvp/gameplay_loop_common.py`
- `tools/mvp/mvp_smoke_common.py`
- `tools/mvp/runtime_bundle.py`
- `tools/mvp/stress_gate_common.py`
- `tools/mvp/toolchain_matrix_common.py`
- `tools/mvp/update_sim_common.py`
- `tools/performx/performx.py`
- `tools/release/offline_archive_common.py`
- `tools/review/architecture_graph_bootstrap_common.py`
- `tools/security/trust_strict_common.py`
- `tools/time/time_anchor_common.py`
- `tools/worldgen/worldgen_lock_common.py`
- `tools/xstack/packagingx/dist_build.py`
- `worldgen/core/constraint_commands.py`

## Scorecard

- `tools/worldgen/worldgen_lock_common.py` disposition=`canonical` rank=`1` total_score=`85.24` risk=`HIGH`
- `tools/mvp/baseline_universe_common.py` disposition=`quarantine` rank=`2` total_score=`84.64` risk=`HIGH`
- `tools/mvp/runtime_bundle.py` disposition=`quarantine` rank=`3` total_score=`84.64` risk=`HIGH`
- `tools/mvp/ecosystem_verify_common.py` disposition=`quarantine` rank=`4` total_score=`84.11` risk=`HIGH`
- `tools/release/offline_archive_common.py` disposition=`quarantine` rank=`5` total_score=`83.04` risk=`HIGH`
- `tools/mvp/disaster_suite_common.py` disposition=`quarantine` rank=`6` total_score=`82.26` risk=`HIGH`
- `tools/mvp/gameplay_loop_common.py` disposition=`quarantine` rank=`7` total_score=`82.26` risk=`HIGH`
- `tools/mvp/mvp_smoke_common.py` disposition=`quarantine` rank=`8` total_score=`81.79` risk=`HIGH`
- `tools/mvp/cross_platform_gate_common.py` disposition=`quarantine` rank=`9` total_score=`81.43` risk=`HIGH`
- `tools/data/tool_spice_import.py` disposition=`quarantine` rank=`10` total_score=`79.02` risk=`HIGH`
- `tools/mvp/toolchain_matrix_common.py` disposition=`quarantine` rank=`11` total_score=`77.85` risk=`HIGH`
- `tools/security/trust_strict_common.py` disposition=`quarantine` rank=`12` total_score=`77.8` risk=`HIGH`
- `tools/mvp/stress_gate_common.py` disposition=`quarantine` rank=`13` total_score=`76.49` risk=`HIGH`
- `tools/xstack/packagingx/dist_build.py` disposition=`quarantine` rank=`14` total_score=`76.07` risk=`HIGH`
- `tools/data/tool_srtm_import.py` disposition=`merge` rank=`15` total_score=`74.26` risk=`HIGH`
- `tools/mvp/update_sim_common.py` disposition=`merge` rank=`16` total_score=`70.14` risk=`HIGH`
- `worldgen/core/constraint_commands.py` disposition=`drop` rank=`17` total_score=`68.99` risk=`HIGH`
- `tools/performx/performx.py` disposition=`merge` rank=`18` total_score=`68.93` risk=`HIGH`
- `tools/review/architecture_graph_bootstrap_common.py` disposition=`merge` rank=`19` total_score=`67.64` risk=`HIGH`
- `tools/audit/arch_audit_common.py` disposition=`merge` rank=`20` total_score=`66.07` risk=`HIGH`
- `tools/time/time_anchor_common.py` disposition=`merge` rank=`21` total_score=`66.07` risk=`HIGH`
- `src/release/release_manifest_engine.py` disposition=`drop` rank=`22` total_score=`62.56` risk=`HIGH`
- `src/time/epoch_anchor_engine.py` disposition=`drop` rank=`23` total_score=`52.71` risk=`HIGH`
- `src/validation/validation_engine.py` disposition=`drop` rank=`24` total_score=`50.89` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/STATUS_NOW.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/REPO_INTENT.md, docs/architecture/lockfile.md, docs/architecture/registry_compile.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
