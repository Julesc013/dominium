Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.2317b4ceb819ec1d`

- Symbol: `_geo_hash`
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
- `src/worldgen/earth/water/water_view_engine.py`
- `src/worldgen/earth/wind/wind_field_engine.py`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py`

## Scorecard

- `src/worldgen/earth/climate_field_engine.py` disposition=`canonical` rank=`1` total_score=`59.64` risk=`HIGH`
- `src/worldgen/earth/wind/wind_field_engine.py` disposition=`quarantine` rank=`2` total_score=`56.81` risk=`HIGH`
- `src/worldgen/earth/material/material_proxy_engine.py` disposition=`quarantine` rank=`3` total_score=`55.54` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`quarantine` rank=`4` total_score=`55.54` risk=`HIGH`
- `src/worldgen/earth/tide_field_engine.py` disposition=`quarantine` rank=`5` total_score=`54.55` risk=`HIGH`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py` disposition=`quarantine` rank=`6` total_score=`50.18` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/COMPAT_SEM2_RETRO_AUDIT.md, docs/audit/DOC_INDEX.md, docs/audit/EARTH10_RETRO_AUDIT.md, docs/audit/EARTH2_RETRO_AUDIT.md, docs/audit/EARTH3_RETRO_AUDIT.md`

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
