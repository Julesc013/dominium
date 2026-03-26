Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.3c317302aa5f5da2`

- Symbol: `_repo_abs`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/worldgen/worldgen_lock_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/validation/validation_engine.py`
- `tools/audit/arch_audit_common.py`
- `tools/convergence/convergence_gate_common.py`
- `tools/mvp/baseline_universe_common.py`
- `tools/mvp/cross_platform_gate_common.py`
- `tools/mvp/disaster_suite_common.py`
- `tools/mvp/ecosystem_verify_common.py`
- `tools/mvp/gameplay_loop_common.py`
- `tools/mvp/mvp_smoke_common.py`
- `tools/mvp/stress_gate_common.py`
- `tools/mvp/toolchain_matrix_common.py`
- `tools/mvp/update_sim_common.py`
- `tools/release/dist_final_common.py`
- `tools/release/offline_archive_common.py`
- `tools/release/scope_freeze_common.py`
- `tools/release/ui_reconcile_common.py`
- `tools/review/architecture_graph_bootstrap_common.py`
- `tools/review/doc_inventory_common.py`
- `tools/review/repo_inventory_common.py`
- `tools/security/trust_strict_common.py`
- `tools/time/time_anchor_common.py`
- `tools/worldgen/worldgen_lock_common.py`

## Scorecard

- `tools/worldgen/worldgen_lock_common.py` disposition=`canonical` rank=`1` total_score=`71.55` risk=`HIGH`
- `tools/release/dist_final_common.py` disposition=`quarantine` rank=`2` total_score=`70.48` risk=`HIGH`
- `tools/review/doc_inventory_common.py` disposition=`quarantine` rank=`3` total_score=`68.92` risk=`HIGH`
- `tools/mvp/cross_platform_gate_common.py` disposition=`quarantine` rank=`4` total_score=`67.74` risk=`HIGH`
- `tools/release/offline_archive_common.py` disposition=`quarantine` rank=`5` total_score=`66.97` risk=`HIGH`
- `tools/mvp/baseline_universe_common.py` disposition=`quarantine` rank=`6` total_score=`66.79` risk=`HIGH`
- `tools/mvp/ecosystem_verify_common.py` disposition=`quarantine` rank=`7` total_score=`66.25` risk=`HIGH`
- `tools/mvp/disaster_suite_common.py` disposition=`quarantine` rank=`8` total_score=`65.6` risk=`HIGH`
- `tools/mvp/gameplay_loop_common.py` disposition=`quarantine` rank=`9` total_score=`65.6` risk=`HIGH`
- `tools/mvp/toolchain_matrix_common.py` disposition=`quarantine` rank=`10` total_score=`64.75` risk=`HIGH`
- `tools/mvp/update_sim_common.py` disposition=`quarantine` rank=`11` total_score=`63.6` risk=`HIGH`
- `tools/mvp/mvp_smoke_common.py` disposition=`quarantine` rank=`12` total_score=`63.33` risk=`HIGH`
- `tools/release/scope_freeze_common.py` disposition=`quarantine` rank=`13` total_score=`63.18` risk=`HIGH`
- `tools/mvp/stress_gate_common.py` disposition=`quarantine` rank=`14` total_score=`62.8` risk=`HIGH`
- `tools/security/trust_strict_common.py` disposition=`quarantine` rank=`15` total_score=`62.32` risk=`HIGH`
- `tools/release/ui_reconcile_common.py` disposition=`quarantine` rank=`16` total_score=`61.56` risk=`HIGH`
- `tools/review/architecture_graph_bootstrap_common.py` disposition=`merge` rank=`17` total_score=`61.46` risk=`HIGH`
- `tools/convergence/convergence_gate_common.py` disposition=`merge` rank=`18` total_score=`59.7` risk=`HIGH`
- `tools/review/repo_inventory_common.py` disposition=`merge` rank=`19` total_score=`56.83` risk=`HIGH`
- `tools/audit/arch_audit_common.py` disposition=`merge` rank=`20` total_score=`53.57` risk=`HIGH`
- `tools/time/time_anchor_common.py` disposition=`merge` rank=`21` total_score=`47.62` risk=`HIGH`
- `src/validation/validation_engine.py` disposition=`merge` rank=`22` total_score=`41.37` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
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
