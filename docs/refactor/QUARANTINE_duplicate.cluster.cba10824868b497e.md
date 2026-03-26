Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.cba10824868b497e`

- Symbol: `_load_fixture`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_session_script_teleport_all_indices.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_earth_tile_roi_selection_determinism.py`
- `tools/xstack/testx/tests/test_no_truth_leak_outside_observer_profile.py`
- `tools/xstack/testx/tests/test_observer_real_data_path_hash.py`
- `tools/xstack/testx/tests/test_session_region_conservation.py`
- `tools/xstack/testx/tests/test_session_script_invalid_target_refusal.py`
- `tools/xstack/testx/tests/test_session_script_teleport_all_indices.py`

## Scorecard

- `tools/xstack/testx/tests/test_session_script_teleport_all_indices.py` disposition=`canonical` rank=`1` total_score=`70.5` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_script_invalid_target_refusal.py` disposition=`quarantine` rank=`2` total_score=`64.77` risk=`HIGH`
- `tools/xstack/testx/tests/test_no_truth_leak_outside_observer_profile.py` disposition=`quarantine` rank=`3` total_score=`62.17` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_region_conservation.py` disposition=`quarantine` rank=`4` total_score=`61.2` risk=`HIGH`
- `tools/xstack/testx/tests/test_observer_real_data_path_hash.py` disposition=`drop` rank=`5` total_score=`60.01` risk=`HIGH`
- `tools/xstack/testx/tests/test_earth_tile_roi_selection_determinism.py` disposition=`drop` rank=`6` total_score=`59.18` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/roadmap/milestone_lab_galaxy.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
