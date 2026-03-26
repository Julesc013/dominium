Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.5b0a023fe6353d98`

- Symbol: `_norm_rel`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/release/dist_final_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `setup/packages/scripts/diagnostics/make_support_bundle.py`
- `setup/packages/scripts/packaging/make_deterministic_archive.py`
- `setup/packages/scripts/packaging/pipeline.py`
- `setup/packages/scripts/packaging/windows/generate_dominium_setup_wxs.py`
- `setup/packages/scripts/packaging/windows/generate_dominium_wxs.py`
- `src/appshell/paths/virtual_paths.py`
- `src/archive/deterministic_bundle.py`
- `src/governance/governance_profile.py`
- `src/lib/bundle/bundle_manifest.py`
- `src/lib/install/install_discovery_engine.py`
- `src/lib/store/reachability_engine.py`
- `src/meta/identity/identity_validator.py`
- `src/release/archive_policy.py`
- `src/release/release_manifest_engine.py`
- `src/release/update_resolver.py`
- `tools/compat/migration_lifecycle_common.py`
- `tools/dist/clean_room_common.py`
- `tools/dist/dist6_interop_common.py`
- `tools/dist/dist_platform_matrix_common.py`
- `tools/dist/dist_verify_common.py`
- `tools/engine/concurrency_contract_common.py`
- `tools/engine/numeric_discipline_common.py`
- `tools/governance/governance_model_common.py`
- `tools/lib/store_gc_common.py`
- `tools/meta/identity_common.py`
- `tools/meta/observability_common.py`
- `tools/mvp/toolchain_matrix_common.py`
- `tools/perf/performance_envelope_common.py`
- `tools/release/arch_matrix_common.py`
- `tools/release/archive_policy_common.py`
- `tools/release/component_graph_common.py`
- `tools/release/dist_final_common.py`
- `tools/release/distribution_model_common.py`
- `tools/release/release_index_policy_common.py`
- `tools/release/update_model_common.py`
- `tools/review/architecture_graph_bootstrap_common.py`
- `tools/security/trust_model_common.py`

## Scorecard

- `tools/release/dist_final_common.py` disposition=`canonical` rank=`1` total_score=`88.33` risk=`HIGH`
- `tools/meta/identity_common.py` disposition=`quarantine` rank=`2` total_score=`87.38` risk=`HIGH`
- `tools/release/component_graph_common.py` disposition=`quarantine` rank=`3` total_score=`87.38` risk=`HIGH`
- `tools/dist/dist_verify_common.py` disposition=`quarantine` rank=`4` total_score=`87.32` risk=`HIGH`
- `tools/dist/clean_room_common.py` disposition=`quarantine` rank=`5` total_score=`85.89` risk=`HIGH`
- `tools/release/release_index_policy_common.py` disposition=`quarantine` rank=`6` total_score=`85.83` risk=`HIGH`
- `tools/release/arch_matrix_common.py` disposition=`quarantine` rank=`7` total_score=`84.76` risk=`HIGH`
- `tools/compat/migration_lifecycle_common.py` disposition=`quarantine` rank=`8` total_score=`84.64` risk=`HIGH`
- `tools/release/archive_policy_common.py` disposition=`quarantine` rank=`9` total_score=`84.64` risk=`HIGH`
- `tools/release/update_model_common.py` disposition=`quarantine` rank=`10` total_score=`84.64` risk=`HIGH`
- `tools/meta/observability_common.py` disposition=`quarantine` rank=`11` total_score=`84.29` risk=`HIGH`
- `tools/lib/store_gc_common.py` disposition=`quarantine` rank=`12` total_score=`83.57` risk=`HIGH`
- `tools/security/trust_model_common.py` disposition=`quarantine` rank=`13` total_score=`83.16` risk=`HIGH`
- `tools/governance/governance_model_common.py` disposition=`quarantine` rank=`14` total_score=`82.5` risk=`HIGH`
- `tools/dist/dist6_interop_common.py` disposition=`merge` rank=`15` total_score=`78.21` risk=`HIGH`
- `tools/mvp/toolchain_matrix_common.py` disposition=`merge` rank=`16` total_score=`77.85` risk=`HIGH`
- `tools/perf/performance_envelope_common.py` disposition=`merge` rank=`17` total_score=`76.01` risk=`HIGH`
- `tools/dist/dist_platform_matrix_common.py` disposition=`merge` rank=`18` total_score=`75.89` risk=`HIGH`
- `src/archive/deterministic_bundle.py` disposition=`drop` rank=`19` total_score=`74.94` risk=`HIGH`
- `tools/engine/concurrency_contract_common.py` disposition=`merge` rank=`20` total_score=`74.32` risk=`HIGH`
- `src/appshell/paths/virtual_paths.py` disposition=`drop` rank=`21` total_score=`73.87` risk=`HIGH`
- `src/governance/governance_profile.py` disposition=`drop` rank=`22` total_score=`73.87` risk=`HIGH`
- `src/lib/install/install_discovery_engine.py` disposition=`merge` rank=`23` total_score=`73.09` risk=`HIGH`
- `src/release/archive_policy.py` disposition=`drop` rank=`24` total_score=`72.38` risk=`HIGH`
- `tools/release/distribution_model_common.py` disposition=`merge` rank=`25` total_score=`72.02` risk=`HIGH`
- `setup/packages/scripts/packaging/pipeline.py` disposition=`drop` rank=`26` total_score=`70.55` risk=`HIGH`
- `src/meta/identity/identity_validator.py` disposition=`drop` rank=`27` total_score=`69.64` risk=`HIGH`
- `tools/engine/numeric_discipline_common.py` disposition=`merge` rank=`28` total_score=`68.94` risk=`HIGH`
- `tools/review/architecture_graph_bootstrap_common.py` disposition=`merge` rank=`29` total_score=`67.64` risk=`HIGH`
- `setup/packages/scripts/diagnostics/make_support_bundle.py` disposition=`drop` rank=`30` total_score=`65.25` risk=`HIGH`
- `setup/packages/scripts/packaging/make_deterministic_archive.py` disposition=`drop` rank=`31` total_score=`64.19` risk=`HIGH`
- `src/release/release_manifest_engine.py` disposition=`drop` rank=`32` total_score=`62.56` risk=`HIGH`
- `setup/packages/scripts/packaging/windows/generate_dominium_setup_wxs.py` disposition=`drop` rank=`33` total_score=`58.11` risk=`HIGH`
- `setup/packages/scripts/packaging/windows/generate_dominium_wxs.py` disposition=`drop` rank=`34` total_score=`58.11` risk=`HIGH`
- `src/lib/store/reachability_engine.py` disposition=`drop` rank=`35` total_score=`54.29` risk=`HIGH`
- `src/release/update_resolver.py` disposition=`drop` rank=`36` total_score=`54.29` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`merge` rank=`37` total_score=`46.76` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/STATUS_NOW.md, docs/XSTACK.md, docs/architecture/CANON_INDEX.md, docs/architecture/session_lifecycle.md, docs/audit/ARCH_AUDIT2_CONSTITUTION.md, docs/audit/ARCH_AUDIT2_FINAL.md, docs/audit/ARCH_AUDIT2_REPORT.md, docs/audit/ARCH_AUDIT2_RETRO_AUDIT.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
