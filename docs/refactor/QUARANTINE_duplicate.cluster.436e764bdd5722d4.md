Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.436e764bdd5722d4`

- Symbol: `_geo_cell_key_sort_tuple`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/hydrology_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/worldgen/worldgen_engine.py`
- `src/worldgen/earth/hydrology_engine.py`

## Scorecard

- `src/worldgen/earth/hydrology_engine.py` disposition=`canonical` rank=`1` total_score=`58.1` risk=`HIGH`
- `src/geo/worldgen/worldgen_engine.py` disposition=`quarantine` rank=`2` total_score=`57.74` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/audit/EARTH10_RETRO_AUDIT.md, docs/audit/EARTH1_RETRO_AUDIT.md, docs/audit/EARTH6_RETRO_AUDIT.md, docs/audit/EARTH_HYDROLOGY_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md`

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
