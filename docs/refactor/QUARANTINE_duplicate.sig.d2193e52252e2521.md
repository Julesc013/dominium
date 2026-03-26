Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d2193e52252e2521`

- Symbol: `_clamp`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/tide_phase_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/astro/ephemeris/kepler_proxy_engine.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/embodiment/collision/macro_heightfield_provider.py`
- `src/embodiment/movement/friction_model.py`
- `src/fluid/network/fluid_network_engine.py`
- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/earth/earth_surface_generator.py`
- `src/worldgen/earth/hydrology_engine.py`
- `src/worldgen/earth/lighting/horizon_shadow_engine.py`
- `src/worldgen/earth/lighting/illumination_engine.py`
- `src/worldgen/earth/material/material_proxy_engine.py`
- `src/worldgen/earth/season_phase_engine.py`
- `src/worldgen/earth/sky/astronomy_proxy_engine.py`
- `src/worldgen/earth/sky/sky_gradient_model.py`
- `src/worldgen/earth/sky/sky_view_engine.py`
- `src/worldgen/earth/sky/starfield_generator.py`
- `src/worldgen/earth/tide_field_engine.py`
- `src/worldgen/earth/tide_phase_engine.py`
- `src/worldgen/earth/water/water_view_engine.py`
- `src/worldgen/earth/wind/wind_field_engine.py`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py`
- `src/worldgen/mw/insolation_proxy.py`
- `src/worldgen/mw/mw_surface_refiner_l3.py`

## Scorecard

- `src/worldgen/earth/tide_phase_engine.py` disposition=`canonical` rank=`1` total_score=`59.79` risk=`HIGH`
- `src/worldgen/earth/climate_field_engine.py` disposition=`quarantine` rank=`2` total_score=`57.71` risk=`HIGH`
- `src/worldgen/earth/season_phase_engine.py` disposition=`quarantine` rank=`3` total_score=`56.98` risk=`HIGH`
- `src/worldgen/earth/earth_surface_generator.py` disposition=`quarantine` rank=`4` total_score=`56.69` risk=`HIGH`
- `src/worldgen/earth/material/material_proxy_engine.py` disposition=`quarantine` rank=`5` total_score=`55.54` risk=`HIGH`
- `src/worldgen/earth/hydrology_engine.py` disposition=`quarantine` rank=`6` total_score=`55.2` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`quarantine` rank=`7` total_score=`53.61` risk=`HIGH`
- `src/worldgen/earth/lighting/horizon_shadow_engine.py` disposition=`quarantine` rank=`8` total_score=`53.37` risk=`HIGH`
- `src/astro/illumination/illumination_geometry_engine.py` disposition=`quarantine` rank=`9` total_score=`53.29` risk=`HIGH`
- `src/worldgen/mw/insolation_proxy.py` disposition=`quarantine` rank=`10` total_score=`53.01` risk=`HIGH`
- `src/embodiment/movement/friction_model.py` disposition=`quarantine` rank=`11` total_score=`52.83` risk=`HIGH`
- `src/worldgen/earth/tide_field_engine.py` disposition=`quarantine` rank=`12` total_score=`52.62` risk=`HIGH`
- `src/worldgen/earth/lighting/illumination_engine.py` disposition=`quarantine` rank=`13` total_score=`52.4` risk=`HIGH`
- `src/worldgen/earth/sky/sky_gradient_model.py` disposition=`quarantine` rank=`14` total_score=`52.4` risk=`HIGH`
- `src/worldgen/earth/wind/wind_field_engine.py` disposition=`quarantine` rank=`15` total_score=`51.08` risk=`HIGH`
- `src/worldgen/earth/sky/sky_view_engine.py` disposition=`quarantine` rank=`16` total_score=`50.86` risk=`HIGH`
- `src/fluid/network/fluid_network_engine.py` disposition=`drop` rank=`17` total_score=`49.46` risk=`HIGH`
- `src/astro/ephemeris/kepler_proxy_engine.py` disposition=`drop` rank=`18` total_score=`49.04` risk=`HIGH`
- `src/worldgen/earth/sky/astronomy_proxy_engine.py` disposition=`drop` rank=`19` total_score=`48.36` risk=`HIGH`
- `src/worldgen/earth/sky/starfield_generator.py` disposition=`drop` rank=`20` total_score=`48.36` risk=`HIGH`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py` disposition=`merge` rank=`21` total_score=`48.25` risk=`HIGH`
- `src/worldgen/mw/mw_surface_refiner_l3.py` disposition=`merge` rank=`22` total_score=`47.84` risk=`HIGH`
- `src/embodiment/collision/macro_heightfield_provider.py` disposition=`merge` rank=`23` total_score=`47.82` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
