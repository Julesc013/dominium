Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.2bfe48ec2fc3c088`

- Symbol: `_round_div_away_from_zero`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/core/graph/network_graph_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/astro/ephemeris/kepler_proxy_engine.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/core/flow/flow_engine.py`
- `src/core/graph/network_graph_engine.py`
- `src/core/spatial/spatial_engine.py`
- `src/geo/frame/frame_engine.py`
- `src/materials/composition_engine.py`
- `src/materials/dimension_engine.py`

## Scorecard

- `src/core/graph/network_graph_engine.py` disposition=`canonical` rank=`1` total_score=`59.41` risk=`HIGH`
- `src/materials/dimension_engine.py` disposition=`quarantine` rank=`2` total_score=`59.41` risk=`HIGH`
- `src/core/spatial/spatial_engine.py` disposition=`quarantine` rank=`3` total_score=`56.19` risk=`HIGH`
- `src/materials/composition_engine.py` disposition=`quarantine` rank=`4` total_score=`55.71` risk=`HIGH`
- `src/geo/frame/frame_engine.py` disposition=`quarantine` rank=`5` total_score=`55.36` risk=`HIGH`
- `src/core/flow/flow_engine.py` disposition=`quarantine` rank=`6` total_score=`53.33` risk=`HIGH`
- `src/astro/illumination/illumination_geometry_engine.py` disposition=`quarantine` rank=`7` total_score=`51.19` risk=`HIGH`
- `src/astro/ephemeris/kepler_proxy_engine.py` disposition=`drop` rank=`8` total_score=`48.87` risk=`HIGH`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
