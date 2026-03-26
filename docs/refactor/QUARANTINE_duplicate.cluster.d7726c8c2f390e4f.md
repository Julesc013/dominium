Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.d7726c8c2f390e4f`

- Symbol: `_geo_cell_key_hash`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/path/shard_route_planner.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/path/path_engine.py`
- `src/geo/path/shard_route_planner.py`

## Scorecard

- `src/geo/path/shard_route_planner.py` disposition=`canonical` rank=`1` total_score=`52.21` risk=`HIGH`
- `src/geo/path/path_engine.py` disposition=`quarantine` rank=`2` total_score=`50.42` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO0_RETRO_AUDIT.md, docs/audit/GEO6_RETRO_AUDIT.md, docs/audit/GEO8_RETRO_AUDIT.md, docs/audit/GEO_CONSTITUTION_BASELINE.md, docs/audit/GEO_FIELD_BINDING_BASELINE.md, docs/audit/GEO_GEOMETRY_EDIT_BASELINE.md, docs/audit/GEO_PATHING_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md`

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
