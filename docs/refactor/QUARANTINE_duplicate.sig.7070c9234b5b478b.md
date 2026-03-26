Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7070c9234b5b478b`

- Symbol: `build_direction_position_ref`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/astro/illumination/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/astro/illumination/__init__.py`
- `src/astro/illumination/illumination_geometry_engine.py`

## Scorecard

- `src/astro/illumination/__init__.py` disposition=`canonical` rank=`1` total_score=`54.69` risk=`HIGH`
- `src/astro/illumination/illumination_geometry_engine.py` disposition=`quarantine` rank=`2` total_score=`52.09` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/ILLUMINATION_GEOMETRY_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/worldgen/EARTH_SKY_STARFIELD_MODEL.md`

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
