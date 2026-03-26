Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f99e8b2a50d7dab4`

- Symbol: `_geo_distance_mm`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/mobility/geometry/geometry_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/mobility/geometry/geometry_engine.py`
- `src/mobility/micro/constrained_motion_solver.py`

## Scorecard

- `src/mobility/geometry/geometry_engine.py` disposition=`canonical` rank=`1` total_score=`51.85` risk=`HIGH`
- `src/mobility/micro/constrained_motion_solver.py` disposition=`quarantine` rank=`2` total_score=`48.79` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EARTH1_RETRO_AUDIT.md, docs/audit/GEO0_RETRO_AUDIT.md, docs/audit/GEO10_RETRO_AUDIT.md, docs/audit/GEO3_RETRO_AUDIT.md, docs/audit/GEO6_RETRO_AUDIT.md, docs/audit/GEO_FINAL_BASELINE.md, docs/audit/GEO_METRIC_BASELINE.md, docs/audit/GEO_PATHING_BASELINE.md`

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
