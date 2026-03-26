Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.89783d3d959ad798`

- Symbol: `_registry_payload`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/earth/water/water_view_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/astro/ephemeris/kepler_proxy_engine.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/embodiment/collision/macro_heightfield_provider.py`
- `src/geo/edit/geometry_state_engine.py`
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

- `src/worldgen/earth/water/water_view_engine.py` disposition=`canonical` rank=`1` total_score=`69.82` risk=`HIGH`
- `src/worldgen/mw/mw_cell_generator.py` disposition=`quarantine` rank=`2` total_score=`68.39` risk=`HIGH`
- `src/worldgen/earth/wind/wind_field_engine.py` disposition=`quarantine` rank=`3` total_score=`64.46` risk=`HIGH`
- `src/astro/illumination/illumination_geometry_engine.py` disposition=`quarantine` rank=`4` total_score=`61.9` risk=`HIGH`
- `src/worldgen/earth/climate_field_engine.py` disposition=`merge` rank=`5` total_score=`59.64` risk=`HIGH`
- `src/worldgen/mw/system_query_engine.py` disposition=`merge` rank=`6` total_score=`59.05` risk=`HIGH`
- `src/worldgen/earth/hydrology_engine.py` disposition=`merge` rank=`7` total_score=`58.1` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`drop` rank=`8` total_score=`57.56` risk=`HIGH`
- `src/worldgen/earth/lighting/illumination_engine.py` disposition=`merge` rank=`9` total_score=`57.23` risk=`HIGH`
- `src/worldgen/mw/mw_surface_refiner_l3.py` disposition=`drop` rank=`10` total_score=`57.2` risk=`HIGH`
- `src/worldgen/mw/mw_system_refiner_l2.py` disposition=`drop` rank=`11` total_score=`57.06` risk=`HIGH`
- `src/worldgen/earth/tide_field_engine.py` disposition=`drop` rank=`12` total_score=`56.48` risk=`HIGH`
- `src/worldgen/earth/lighting/horizon_shadow_engine.py` disposition=`merge` rank=`13` total_score=`56.26` risk=`HIGH`
- `src/worldgen/earth/material/material_proxy_engine.py` disposition=`merge` rank=`14` total_score=`55.54` risk=`HIGH`
- `src/worldgen/earth/sky/starfield_generator.py` disposition=`merge` rank=`15` total_score=`54.14` risk=`HIGH`
- `src/worldgen/earth/sky/sky_view_engine.py` disposition=`merge` rank=`16` total_score=`53.75` risk=`HIGH`
- `src/astro/ephemeris/kepler_proxy_engine.py` disposition=`drop` rank=`17` total_score=`52.89` risk=`HIGH`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py` disposition=`drop` rank=`18` total_score=`51.14` risk=`HIGH`
- `src/embodiment/collision/macro_heightfield_provider.py` disposition=`drop` rank=`19` total_score=`49.75` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/audit/ARCH_AUDIT_CONSTITUTION.md, docs/audit/CANON_MAP.md, docs/audit/COMPARTMENT_FLOWS_BASELINE.md, docs/audit/COMPAT_SEM2_RETRO_AUDIT.md, docs/audit/CORE_ABSTRACTIONS_BASELINE.md, docs/audit/DOC_INDEX.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
