Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.8d3430f714445a5e`

- Symbol: `DEFAULT_TIDE_PARAMS_ID`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/worldgen/earth/__init__.py`
- `src/worldgen/earth/tide_field_engine.py`

## Scorecard

- `src/worldgen/earth/__init__.py` disposition=`canonical` rank=`1` total_score=`59.88` risk=`HIGH`
- `src/worldgen/earth/tide_field_engine.py` disposition=`quarantine` rank=`2` total_score=`54.55` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EARTH_SEASONAL_CLIMATE_BASELINE.md, docs/audit/EARTH_SKY_STARFIELD_BASELINE.md, docs/audit/EARTH_TIDE_PROXY_BASELINE.md, docs/audit/META_STABILITY0_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SOL1_RETRO_AUDIT.md, docs/audit/STABILITY_CLASSIFICATION_BASELINE.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md`

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
