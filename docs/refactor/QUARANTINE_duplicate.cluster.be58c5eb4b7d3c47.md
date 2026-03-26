Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.be58c5eb4b7d3c47`

- Symbol: `_iter_lines`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/worldgen/gal0_audit_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `deprecate, quarantine`

## Competing Files

- `tools/auditx/analyzers/e33_nondeterministic_cohort_mapping_smell.py`
- `tools/auditx/analyzers/e34_order_bypass_smell.py`
- `tools/auditx/analyzers/e35_role_escalation_smell.py`
- `tools/auditx/analyzers/e36_render_truth_leak_smell.py`
- `tools/auditx/analyzers/e39_nondeterministic_rate_usage_smell.py`
- `tools/auditx/analyzers/e40_physics_assumption_smell.py`
- `tools/auditx/analyzers/e44_wall_clock_time_usage_smell.py`
- `tools/auditx/analyzers/e45_nondeterministic_checkpoint_smell.py`
- `tools/auditx/analyzers/e47_nondeterministic_arbitration_smell.py`
- `tools/auditx/analyzers/e48_performance_nondeterminism_smell.py`
- `tools/auditx/analyzers/e50_renderer_truth_leak_smell.py`
- `tools/auditx/analyzers/e52_interaction_bypass_smell.py`
- `tools/auditx/analyzers/e53_preview_info_leak_smell.py`
- `tools/auditx/analyzers/e54_platform_leak_smell.py`
- `tools/auditx/analyzers/e55_renderer_backend_truth_leak_smell.py`
- `tools/auditx/analyzers/e56_raw_float_in_invariant_smell.py`
- `tools/auditx/analyzers/e58_hardcoded_periodic_table_smell.py`
- `tools/auditx/analyzers/e60_hardcoded_blueprint_smell.py`
- `tools/auditx/analyzers/e62_silent_shipment_smell.py`
- `tools/auditx/analyzers/e64_silent_construction_smell.py`
- `tools/auditx/analyzers/e66_silent_failure_smell.py`
- `tools/auditx/analyzers/e67_nondeterministic_hazard_smell.py`
- `tools/worldgen/earth10_audit_common.py`
- `tools/worldgen/gal0_audit_common.py`

## Scorecard

- `tools/worldgen/gal0_audit_common.py` disposition=`canonical` rank=`1` total_score=`61.64` risk=`HIGH`
- `tools/worldgen/earth10_audit_common.py` disposition=`quarantine` rank=`2` total_score=`61.11` risk=`HIGH`
- `tools/auditx/analyzers/e34_order_bypass_smell.py` disposition=`quarantine` rank=`3` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e35_role_escalation_smell.py` disposition=`quarantine` rank=`4` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e36_render_truth_leak_smell.py` disposition=`quarantine` rank=`5` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e40_physics_assumption_smell.py` disposition=`quarantine` rank=`6` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e50_renderer_truth_leak_smell.py` disposition=`quarantine` rank=`7` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e52_interaction_bypass_smell.py` disposition=`quarantine` rank=`8` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e53_preview_info_leak_smell.py` disposition=`quarantine` rank=`9` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e54_platform_leak_smell.py` disposition=`quarantine` rank=`10` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e55_renderer_backend_truth_leak_smell.py` disposition=`quarantine` rank=`11` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e56_raw_float_in_invariant_smell.py` disposition=`quarantine` rank=`12` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e58_hardcoded_periodic_table_smell.py` disposition=`quarantine` rank=`13` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e60_hardcoded_blueprint_smell.py` disposition=`quarantine` rank=`14` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e62_silent_shipment_smell.py` disposition=`quarantine` rank=`15` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e64_silent_construction_smell.py` disposition=`quarantine` rank=`16` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e66_silent_failure_smell.py` disposition=`quarantine` rank=`17` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e33_nondeterministic_cohort_mapping_smell.py` disposition=`drop` rank=`18` total_score=`50.83` risk=`HIGH`
- `tools/auditx/analyzers/e39_nondeterministic_rate_usage_smell.py` disposition=`drop` rank=`19` total_score=`47.98` risk=`HIGH`
- `tools/auditx/analyzers/e45_nondeterministic_checkpoint_smell.py` disposition=`drop` rank=`20` total_score=`47.98` risk=`HIGH`
- `tools/auditx/analyzers/e47_nondeterministic_arbitration_smell.py` disposition=`drop` rank=`21` total_score=`47.98` risk=`HIGH`
- `tools/auditx/analyzers/e44_wall_clock_time_usage_smell.py` disposition=`drop` rank=`22` total_score=`45.12` risk=`HIGH`
- `tools/auditx/analyzers/e48_performance_nondeterminism_smell.py` disposition=`drop` rank=`23` total_score=`35.12` risk=`HIGH`
- `tools/auditx/analyzers/e67_nondeterministic_hazard_smell.py` disposition=`drop` rank=`24` total_score=`35.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
