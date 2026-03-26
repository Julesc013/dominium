Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.efe70615463e13c9`

- Symbol: `_cache_store`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/client/ui/map_views.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/astro/views/orbit_view_engine.py`
- `src/client/ui/map_views.py`
- `src/geo/kernel/geo_kernel.py`
- `src/geo/worldgen/worldgen_engine.py`
- `src/worldgen/earth/lighting/lighting_view_engine.py`
- `src/worldgen/earth/sky/sky_view_engine.py`
- `src/worldgen/earth/water/water_view_engine.py`

## Scorecard

- `src/client/ui/map_views.py` disposition=`canonical` rank=`1` total_score=`69.23` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`quarantine` rank=`2` total_score=`65.06` risk=`HIGH`
- `src/geo/worldgen/worldgen_engine.py` disposition=`drop` rank=`3` total_score=`57.74` risk=`HIGH`
- `src/geo/kernel/geo_kernel.py` disposition=`merge` rank=`4` total_score=`57.62` risk=`HIGH`
- `src/worldgen/earth/sky/sky_view_engine.py` disposition=`drop` rank=`5` total_score=`53.75` risk=`HIGH`
- `src/worldgen/earth/lighting/lighting_view_engine.py` disposition=`drop` rank=`6` total_score=`52.51` risk=`HIGH`
- `src/astro/views/orbit_view_engine.py` disposition=`drop` rank=`7` total_score=`52.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/DEMOGRAPHY_OPTIONALITY_BASELINE.md, docs/audit/EARTH9_RETRO_AUDIT.md, docs/audit/ELEC4_RETRO_AUDIT.md, docs/audit/ELECTRICAL_PROTECTION_BASELINE.md, docs/audit/GEO_FINAL_BASELINE.md, docs/audit/GEO_PROJECTION_LENS_BASELINE.md, docs/audit/INSPECTION_SYSTEM_BASELINE.md, docs/audit/INTERIOR_DIEGETIC_INSPECTION_BASELINE.md`

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
