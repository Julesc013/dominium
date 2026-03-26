Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.8f48eeb3513c8c2c`

- Symbol: `geometry_add_volume`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/edit/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/__init__.py`
- `src/geo/edit/__init__.py`
- `src/geo/edit/geometry_state_engine.py`

## Scorecard

- `src/geo/edit/__init__.py` disposition=`canonical` rank=`1` total_score=`63.15` risk=`HIGH`
- `src/geo/__init__.py` disposition=`quarantine` rank=`2` total_score=`59.88` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`quarantine` rank=`3` total_score=`53.7` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO_GEOMETRY_EDIT_BASELINE.md, docs/audit/MOB1_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/embodiment/MVP_TOOLBELT_MODEL.md, docs/geo/GEOMETRY_EDIT_CONTRACT.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/worldgen/EARTH_HYDROLOGY_MODEL.md`

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
