Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7e7e0f5c93afd04e`

- Symbol: `_seed_state`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_network_create_deterministic.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_cure_progress_deterministic.py`
- `tools/xstack/testx/tests/test_network_create_deterministic.py`
- `tools/xstack/testx/tests/test_no_motion_sim_side_effects.py`
- `tools/xstack/testx/tests/test_phase_transform_emits_provenance.py`
- `tools/xstack/testx/tests/test_routing_deterministic_tie_break.py`
- `tools/xstack/testx/tests/test_spec_compatibility_refusal.py`
- `tools/xstack/testx/tests/test_spec_noncompliance_refusal.py`
- `tools/xstack/testx/tests/test_switch_state_changes_route_availability.py`
- `tools/xstack/testx/tests/test_vehicle_ports_pose_interior_refs_valid.py`
- `tools/xstack/testx/tests/test_vehicle_register_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_network_create_deterministic.py` disposition=`canonical` rank=`1` total_score=`71.58` risk=`HIGH`
- `tools/xstack/testx/tests/test_vehicle_register_deterministic.py` disposition=`quarantine` rank=`2` total_score=`70.26` risk=`HIGH`
- `tools/xstack/testx/tests/test_spec_compatibility_refusal.py` disposition=`quarantine` rank=`3` total_score=`65.92` risk=`HIGH`
- `tools/xstack/testx/tests/test_routing_deterministic_tie_break.py` disposition=`quarantine` rank=`4` total_score=`65.86` risk=`HIGH`
- `tools/xstack/testx/tests/test_vehicle_ports_pose_interior_refs_valid.py` disposition=`quarantine` rank=`5` total_score=`63.12` risk=`HIGH`
- `tools/xstack/testx/tests/test_cure_progress_deterministic.py` disposition=`merge` rank=`6` total_score=`58.71` risk=`HIGH`
- `tools/xstack/testx/tests/test_no_motion_sim_side_effects.py` disposition=`drop` rank=`7` total_score=`58.71` risk=`HIGH`
- `tools/xstack/testx/tests/test_switch_state_changes_route_availability.py` disposition=`drop` rank=`8` total_score=`58.71` risk=`HIGH`
- `tools/xstack/testx/tests/test_spec_noncompliance_refusal.py` disposition=`drop` rank=`9` total_score=`57.98` risk=`HIGH`
- `tools/xstack/testx/tests/test_phase_transform_emits_provenance.py` disposition=`merge` rank=`10` total_score=`57.75` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
