Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.413a3b65c953f813`

- Symbol: `_sorted_geo_cell_keys`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/hydrology_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/edit/geometry_state_engine.py`
- `src/worldgen/earth/hydrology_engine.py`
- `src/worldgen/earth/water/water_view_engine.py`

## Scorecard

- `src/worldgen/earth/hydrology_engine.py` disposition=`canonical` rank=`1` total_score=`58.1` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`quarantine` rank=`2` total_score=`57.56` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`quarantine` rank=`3` total_score=`54.57` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/COMPAT_SEM2_RETRO_AUDIT.md, docs/audit/EARTH10_RETRO_AUDIT.md, docs/audit/EARTH6_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md, docs/worldgen/WORLDGEN_LOCK_v0_0_0.md`

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
