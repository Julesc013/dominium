Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.7596392767c8182e`

- Symbol: `REFUSAL_GEO_RENDER_REBASE_INVALID`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/render/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/render/__init__.py`
- `src/geo/render/floating_origin_policy.py`

## Scorecard

- `src/geo/render/__init__.py` disposition=`canonical` rank=`1` total_score=`45.62` risk=`HIGH`
- `src/geo/render/floating_origin_policy.py` disposition=`quarantine` rank=`2` total_score=`42.7` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
