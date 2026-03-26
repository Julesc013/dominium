Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d976bae2509fcaaf`

- Symbol: `_cache_lookup`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/client/ui/map_views.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/astro/views/orbit_view_engine.py`
- `src/client/ui/map_views.py`
- `src/geo/kernel/geo_kernel.py`
- `src/geo/worldgen/worldgen_engine.py`
- `src/worldgen/earth/lighting/lighting_view_engine.py`
- `src/worldgen/earth/sky/sky_view_engine.py`
- `src/worldgen/earth/water/water_view_engine.py`

## Scorecard

- `src/client/ui/map_views.py` disposition=`canonical` rank=`1` total_score=`58.74` risk=`HIGH`
- `src/geo/kernel/geo_kernel.py` disposition=`quarantine` rank=`2` total_score=`57.62` risk=`HIGH`
- `src/geo/worldgen/worldgen_engine.py` disposition=`quarantine` rank=`3` total_score=`54.85` risk=`HIGH`
- `src/astro/views/orbit_view_engine.py` disposition=`quarantine` rank=`4` total_score=`50.29` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`quarantine` rank=`5` total_score=`49.75` risk=`HIGH`
- `src/worldgen/earth/lighting/lighting_view_engine.py` disposition=`drop` rank=`6` total_score=`47.69` risk=`HIGH`
- `src/worldgen/earth/sky/sky_view_engine.py` disposition=`drop` rank=`7` total_score=`47.0` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/geo/GEO_CONSTITUTION.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/SPEC_ACTIONS.md, docs/system/SYSTEM_FORENSICS_MODEL.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
