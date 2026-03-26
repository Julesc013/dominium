Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b462cd504c062d16`

- Symbol: `_registry_payload`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/client/ui/map_views.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/astro/ephemeris/kepler_proxy_engine.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/client/ui/map_views.py`
- `src/embodiment/body/body_system.py`
- `src/embodiment/collision/macro_heightfield_provider.py`
- `src/embodiment/lens/camera_smoothing.py`
- `src/embodiment/lens/lens_engine.py`
- `src/embodiment/movement/jump_process.py`
- `src/embodiment/tools/toolbelt_engine.py`
- `src/geo/edit/geometry_state_engine.py`
- `src/geo/lens/lens_engine.py`
- `src/geo/metric/metric_engine.py`
- `src/geo/overlay/overlay_merge_engine.py`
- `src/geo/projection/projection_engine.py`
- `src/geo/worldgen/worldgen_engine.py`
- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/earth/hydrology_engine.py`
- `src/worldgen/earth/lighting/horizon_shadow_engine.py`
- `src/worldgen/earth/lighting/illumination_engine.py`
- `src/worldgen/earth/material/material_proxy_engine.py`
- `src/worldgen/earth/sky/sky_view_engine.py`
- `src/worldgen/earth/sky/starfield_generator.py`
- `src/worldgen/earth/tide_field_engine.py`
- `src/worldgen/earth/water/water_view_engine.py`
- `src/worldgen/earth/wind/wind_field_engine.py`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py`
- `src/worldgen/mw/mw_cell_generator.py`
- `src/worldgen/mw/mw_surface_refiner_l3.py`
- `src/worldgen/mw/mw_system_refiner_l2.py`
- `src/worldgen/mw/system_query_engine.py`

## Scorecard

- `src/client/ui/map_views.py` disposition=`canonical` rank=`1` total_score=`73.99` risk=`HIGH`
- `src/embodiment/body/body_system.py` disposition=`quarantine` rank=`2` total_score=`71.85` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`quarantine` rank=`3` total_score=`69.82` risk=`HIGH`
- `src/worldgen/mw/mw_cell_generator.py` disposition=`quarantine` rank=`4` total_score=`68.39` risk=`HIGH`
- `src/embodiment/lens/lens_engine.py` disposition=`quarantine` rank=`5` total_score=`67.26` risk=`HIGH`
- `src/geo/worldgen/worldgen_engine.py` disposition=`quarantine` rank=`6` total_score=`67.26` risk=`HIGH`
- `src/worldgen/earth/wind/wind_field_engine.py` disposition=`quarantine` rank=`7` total_score=`64.46` risk=`HIGH`
- `src/geo/metric/metric_engine.py` disposition=`drop` rank=`8` total_score=`63.99` risk=`HIGH`
- `src/astro/illumination/illumination_geometry_engine.py` disposition=`drop` rank=`9` total_score=`61.9` risk=`HIGH`
- `src/geo/lens/lens_engine.py` disposition=`drop` rank=`10` total_score=`60.95` risk=`HIGH`
- `src/worldgen/earth/climate_field_engine.py` disposition=`drop` rank=`11` total_score=`59.64` risk=`HIGH`
- `src/worldgen/mw/system_query_engine.py` disposition=`drop` rank=`12` total_score=`59.05` risk=`HIGH`
- `src/worldgen/earth/hydrology_engine.py` disposition=`drop` rank=`13` total_score=`58.1` risk=`HIGH`
- `src/embodiment/tools/toolbelt_engine.py` disposition=`drop` rank=`14` total_score=`57.87` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`drop` rank=`15` total_score=`57.56` risk=`HIGH`
- `src/worldgen/earth/lighting/illumination_engine.py` disposition=`drop` rank=`16` total_score=`57.23` risk=`HIGH`
- `src/worldgen/mw/mw_surface_refiner_l3.py` disposition=`drop` rank=`17` total_score=`57.2` risk=`HIGH`
- `src/worldgen/mw/mw_system_refiner_l2.py` disposition=`drop` rank=`18` total_score=`57.06` risk=`HIGH`
- `src/geo/projection/projection_engine.py` disposition=`drop` rank=`19` total_score=`56.67` risk=`HIGH`
- `src/worldgen/earth/tide_field_engine.py` disposition=`drop` rank=`20` total_score=`56.48` risk=`HIGH`
- `src/worldgen/earth/lighting/horizon_shadow_engine.py` disposition=`drop` rank=`21` total_score=`56.26` risk=`HIGH`
- `src/embodiment/lens/camera_smoothing.py` disposition=`drop` rank=`22` total_score=`55.73` risk=`HIGH`
- `src/worldgen/earth/material/material_proxy_engine.py` disposition=`drop` rank=`23` total_score=`55.54` risk=`HIGH`
- `src/geo/overlay/overlay_merge_engine.py` disposition=`drop` rank=`24` total_score=`54.94` risk=`HIGH`
- `src/worldgen/earth/sky/starfield_generator.py` disposition=`drop` rank=`25` total_score=`54.14` risk=`HIGH`
- `src/worldgen/earth/sky/sky_view_engine.py` disposition=`drop` rank=`26` total_score=`53.75` risk=`HIGH`
- `src/astro/ephemeris/kepler_proxy_engine.py` disposition=`drop` rank=`27` total_score=`52.89` risk=`HIGH`
- `src/embodiment/movement/jump_process.py` disposition=`drop` rank=`28` total_score=`52.83` risk=`HIGH`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py` disposition=`drop` rank=`29` total_score=`51.14` risk=`HIGH`
- `src/embodiment/collision/macro_heightfield_provider.py` disposition=`drop` rank=`30` total_score=`49.75` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/README.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/LOGGING_AND_TRACING.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/APP_CANON0.md, docs/architecture/CANONICAL_SYSTEM_MAP.md, docs/architecture/CODE_DATA_BOUNDARY.md, docs/architecture/COMPLEXITY_AND_SCALE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
