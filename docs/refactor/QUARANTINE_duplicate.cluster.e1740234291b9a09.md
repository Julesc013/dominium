Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.e1740234291b9a09`

- Symbol: `_round_div_away_from_zero`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/frame/frame_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/astro/ephemeris/kepler_proxy_engine.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/geo/frame/frame_engine.py`

## Scorecard

- `src/geo/frame/frame_engine.py` disposition=`canonical` rank=`1` total_score=`55.36` risk=`HIGH`
- `src/astro/illumination/illumination_geometry_engine.py` disposition=`quarantine` rank=`2` total_score=`51.19` risk=`HIGH`
- `src/astro/ephemeris/kepler_proxy_engine.py` disposition=`quarantine` rank=`3` total_score=`48.87` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/policies/DETERMINISTIC_MATH.md`

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
