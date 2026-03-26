Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.49568c286ae3c6b1`

- Symbol: `_legacy_cell_alias_from_tile_key`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/climate_field_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/earth/material/material_proxy_engine.py`
- `src/worldgen/earth/tide_field_engine.py`
- `src/worldgen/earth/wind/wind_field_engine.py`

## Scorecard

- `src/worldgen/earth/climate_field_engine.py` disposition=`canonical` rank=`1` total_score=`59.64` risk=`HIGH`
- `src/worldgen/earth/tide_field_engine.py` disposition=`quarantine` rank=`2` total_score=`57.44` risk=`HIGH`
- `src/worldgen/earth/material/material_proxy_engine.py` disposition=`quarantine` rank=`3` total_score=`55.54` risk=`HIGH`
- `src/worldgen/earth/wind/wind_field_engine.py` disposition=`quarantine` rank=`4` total_score=`54.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EARTH7_RETRO_AUDIT.md, docs/audit/GEO_IDENTITY_BASELINE.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
