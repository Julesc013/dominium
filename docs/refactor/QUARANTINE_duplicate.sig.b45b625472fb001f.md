Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b45b625472fb001f`

- Symbol: `_states`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_interior_time_warp_large_dt_stable.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_flood_transfer_deterministic.py`
- `tools/xstack/testx/tests/test_interior_time_warp_large_dt_stable.py`
- `tools/xstack/testx/tests/test_pressure_equalization_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_interior_time_warp_large_dt_stable.py` disposition=`canonical` rank=`1` total_score=`58.95` risk=`HIGH`
- `tools/xstack/testx/tests/test_flood_transfer_deterministic.py` disposition=`quarantine` rank=`2` total_score=`56.93` risk=`HIGH`
- `tools/xstack/testx/tests/test_pressure_equalization_deterministic.py` disposition=`quarantine` rank=`3` total_score=`52.62` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
