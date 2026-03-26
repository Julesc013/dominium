Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b5fe8fa6a6069466`

- Symbol: `_safe_rmtree`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/dist/dist_tree_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/dist/dist_tree_common.py`
- `tools/lib/lib_stress_common.py`
- `tools/mvp/disaster_suite_common.py`
- `tools/mvp/mvp_smoke_common.py`
- `tools/mvp/stress_gate_common.py`
- `tools/mvp/update_sim_common.py`
- `tools/release/offline_archive_common.py`
- `tools/time/time_anchor_common.py`

## Scorecard

- `tools/dist/dist_tree_common.py` disposition=`canonical` rank=`1` total_score=`63.21` risk=`HIGH`
- `tools/mvp/disaster_suite_common.py` disposition=`quarantine` rank=`2` total_score=`61.29` risk=`HIGH`
- `tools/mvp/mvp_smoke_common.py` disposition=`quarantine` rank=`3` total_score=`60.36` risk=`HIGH`
- `tools/mvp/stress_gate_common.py` disposition=`quarantine` rank=`4` total_score=`57.89` risk=`HIGH`
- `tools/release/offline_archive_common.py` disposition=`quarantine` rank=`5` total_score=`57.75` risk=`HIGH`
- `tools/lib/lib_stress_common.py` disposition=`quarantine` rank=`6` total_score=`56.79` risk=`HIGH`
- `tools/mvp/update_sim_common.py` disposition=`quarantine` rank=`7` total_score=`55.35` risk=`HIGH`
- `tools/time/time_anchor_common.py` disposition=`merge` rank=`8` total_score=`44.64` risk=`HIGH`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
