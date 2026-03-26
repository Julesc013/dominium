Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.3c1e26d4df6c10ee`

- Symbol: `parse_kv`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/app/scale1_collapse_expand_tests.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/app/mmo1_runtime_tests.py`
- `tests/app/mmo2_ops_tests.py`
- `tests/app/scale1_collapse_expand_tests.py`
- `tests/app/scale2_macro_time_tests.py`
- `tests/app/scale3_budget_tests.py`

## Scorecard

- `tests/app/scale1_collapse_expand_tests.py` disposition=`canonical` rank=`1` total_score=`54.52` risk=`HIGH`
- `tests/app/mmo1_runtime_tests.py` disposition=`quarantine` rank=`2` total_score=`52.14` risk=`HIGH`
- `tests/app/mmo2_ops_tests.py` disposition=`quarantine` rank=`3` total_score=`52.14` risk=`HIGH`
- `tests/app/scale2_macro_time_tests.py` disposition=`quarantine` rank=`4` total_score=`52.14` risk=`HIGH`
- `tests/app/scale3_budget_tests.py` disposition=`quarantine` rank=`5` total_score=`52.14` risk=`HIGH`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
