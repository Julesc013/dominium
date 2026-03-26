Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.eabf43424e7e97f8`

- Symbol: `_policy_context`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_epistemic_redaction_in_view.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_budget_exceeded_triggers_degrade_not_lag.py`
- `tools/xstack/testx/tests/test_capability_inspection_redaction.py`
- `tools/xstack/testx/tests/test_cosmetic_assign_entitlement_required.py`
- `tools/xstack/testx/tests/test_cosmetics_do_not_change_truth_outcomes.py`
- `tools/xstack/testx/tests/test_cost_accounting_deterministic.py`
- `tools/xstack/testx/tests/test_cure_progress_deterministic.py`
- `tools/xstack/testx/tests/test_epistemic_redaction_in_view.py`
- `tools/xstack/testx/tests/test_inspection_cache_reuse.py`
- `tools/xstack/testx/tests/test_inspection_invalidation_on_state_change.py`
- `tools/xstack/testx/tests/test_model_reads_bundle_components.py`
- `tools/xstack/testx/tests/test_output_processes_emitted.py`
- `tools/xstack/testx/tests/test_phase_transform_emits_provenance.py`
- `tools/xstack/testx/tests/test_private_accept_cosmetic_pack.py`
- `tools/xstack/testx/tests/test_ranked_profile_forbids_free_view.py`
- `tools/xstack/testx/tests/test_ranked_refuse_unsigned_cosmetic_pack.py`
- `tools/xstack/testx/tests/test_spec_compatibility_refusal.py`
- `tools/xstack/testx/tests/test_vehicle_register_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_epistemic_redaction_in_view.py` disposition=`canonical` rank=`1` total_score=`76.45` risk=`HIGH`
- `tools/xstack/testx/tests/test_inspection_invalidation_on_state_change.py` disposition=`quarantine` rank=`2` total_score=`72.64` risk=`HIGH`
- `tools/xstack/testx/tests/test_vehicle_register_deterministic.py` disposition=`quarantine` rank=`3` total_score=`70.26` risk=`HIGH`
- `tools/xstack/testx/tests/test_inspection_cache_reuse.py` disposition=`quarantine` rank=`4` total_score=`69.3` risk=`HIGH`
- `tools/xstack/testx/tests/test_cosmetic_assign_entitlement_required.py` disposition=`quarantine` rank=`5` total_score=`66.57` risk=`HIGH`
- `tools/xstack/testx/tests/test_output_processes_emitted.py` disposition=`quarantine` rank=`6` total_score=`66.57` risk=`HIGH`
- `tools/xstack/testx/tests/test_capability_inspection_redaction.py` disposition=`drop` rank=`7` total_score=`64.19` risk=`HIGH`
- `tools/xstack/testx/tests/test_private_accept_cosmetic_pack.py` disposition=`merge` rank=`8` total_score=`64.19` risk=`HIGH`
- `tools/xstack/testx/tests/test_cosmetics_do_not_change_truth_outcomes.py` disposition=`merge` rank=`9` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_model_reads_bundle_components.py` disposition=`merge` rank=`10` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_ranked_profile_forbids_free_view.py` disposition=`merge` rank=`11` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_ranked_refuse_unsigned_cosmetic_pack.py` disposition=`merge` rank=`12` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_spec_compatibility_refusal.py` disposition=`merge` rank=`13` total_score=`62.06` risk=`HIGH`
- `tools/xstack/testx/tests/test_cost_accounting_deterministic.py` disposition=`merge` rank=`14` total_score=`60.74` risk=`HIGH`
- `tools/xstack/testx/tests/test_budget_exceeded_triggers_degrade_not_lag.py` disposition=`drop` rank=`15` total_score=`58.81` risk=`HIGH`
- `tools/xstack/testx/tests/test_cure_progress_deterministic.py` disposition=`merge` rank=`16` total_score=`58.71` risk=`HIGH`
- `tools/xstack/testx/tests/test_phase_transform_emits_provenance.py` disposition=`merge` rank=`17` total_score=`57.75` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CAPABILITY_REGISTRY_BASELINE.md, docs/audit/COMPARTMENT_FLOWS_BASELINE.md, docs/audit/INSPECTION_SYSTEM_BASELINE.md, docs/audit/LOD_EPISTEMIC_INVARIANCE_BASELINE.md, docs/audit/MACRO_MICRO_MAPPING_BASELINE.md, docs/audit/META_INSTR0_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

## Tests Involved

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
