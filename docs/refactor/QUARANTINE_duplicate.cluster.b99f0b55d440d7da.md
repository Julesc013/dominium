Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.b99f0b55d440d7da`

- Symbol: `d_fixed_div_q16_16`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/world/geology_fields.cpp`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/world/climate_fields.cpp`
- `engine/modules/world/geology_fields.cpp`

## Scorecard

- `engine/modules/world/geology_fields.cpp` disposition=`canonical` rank=`1` total_score=`60.71` risk=`HIGH`
- `engine/modules/world/climate_fields.cpp` disposition=`quarantine` rank=`2` total_score=`58.79` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
