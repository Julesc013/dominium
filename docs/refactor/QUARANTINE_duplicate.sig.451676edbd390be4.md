Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.451676edbd390be4`

- Symbol: `_sha256_file`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/core/repo_health.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `setup/packages/scripts/packaging/pipeline.py`
- `setup/packages/scripts/packaging/tests/packaging_validation_test.py`
- `setup/packages/scripts/repro/verify_reproducible_builds.py`
- `src/archive/deterministic_bundle.py`
- `src/lib/store/reachability_engine.py`
- `src/release/release_manifest_engine.py`
- `tools/dist/dist_verify_common.py`
- `tools/mvp/toolchain_matrix_common.py`
- `tools/release/archive_policy_common.py`
- `tools/release/component_graph_common.py`
- `tools/release/offline_archive_common.py`
- `tools/release/update_model_common.py`
- `tools/securex/core/integrity_manifest.py`
- `tools/securex/core/reproducible_build_check.py`
- `tools/system/anb_omega.py`
- `tools/xstack/core/execution_ledger.py`
- `tools/xstack/core/repo_health.py`
- `tools/xstack/packagingx/dist_build.py`
- `tools/xstack/sessionx/time_lineage.py`

## Scorecard

- `tools/xstack/core/repo_health.py` disposition=`canonical` rank=`1` total_score=`79.28` risk=`HIGH`
- `tools/dist/dist_verify_common.py` disposition=`quarantine` rank=`2` total_score=`77.8` risk=`HIGH`
- `tools/securex/core/integrity_manifest.py` disposition=`merge` rank=`3` total_score=`74.46` risk=`HIGH`
- `tools/securex/core/reproducible_build_check.py` disposition=`merge` rank=`4` total_score=`74.1` risk=`HIGH`
- `tools/release/component_graph_common.py` disposition=`merge` rank=`5` total_score=`73.1` risk=`HIGH`
- `tools/release/archive_policy_common.py` disposition=`quarantine` rank=`6` total_score=`72.74` risk=`HIGH`
- `tools/release/offline_archive_common.py` disposition=`merge` rank=`7` total_score=`71.13` risk=`HIGH`
- `tools/xstack/core/execution_ledger.py` disposition=`merge` rank=`8` total_score=`67.92` risk=`HIGH`
- `tools/release/update_model_common.py` disposition=`merge` rank=`9` total_score=`67.38` risk=`HIGH`
- `setup/packages/scripts/packaging/pipeline.py` disposition=`merge` rank=`10` total_score=`66.01` risk=`HIGH`
- `tools/mvp/toolchain_matrix_common.py` disposition=`merge` rank=`11` total_score=`65.94` risk=`HIGH`
- `src/archive/deterministic_bundle.py` disposition=`merge` rank=`12` total_score=`63.04` risk=`HIGH`
- `tools/xstack/sessionx/time_lineage.py` disposition=`drop` rank=`13` total_score=`62.9` risk=`HIGH`
- `setup/packages/scripts/packaging/tests/packaging_validation_test.py` disposition=`drop` rank=`14` total_score=`61.23` risk=`HIGH`
- `setup/packages/scripts/repro/verify_reproducible_builds.py` disposition=`drop` rank=`15` total_score=`58.11` risk=`HIGH`
- `tools/xstack/packagingx/dist_build.py` disposition=`merge` rank=`16` total_score=`56.29` risk=`HIGH`
- `src/release/release_manifest_engine.py` disposition=`merge` rank=`17` total_score=`55.42` risk=`HIGH`
- `src/lib/store/reachability_engine.py` disposition=`drop` rank=`18` total_score=`47.23` risk=`HIGH`
- `tools/system/anb_omega.py` disposition=`drop` rank=`19` total_score=`45.71` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/system/XSTACK_PRODUCTION_FINAL_REPORT.md`

## Tests Involved

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
