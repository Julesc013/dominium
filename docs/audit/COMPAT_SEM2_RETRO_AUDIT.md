Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# COMPAT-SEM-2 Retro Audit

## Scope
- Enumerate current extension-bearing schema surface.
- Identify implicit extension interpretation paths.
- Identify unsorted or unvalidated extension-loading seams.
- Check existing data and packs for namespacing discipline.

## Findings
- Schema surface using `extensions` is pervasive.
  - `schema/`: automated scan found 705 files containing `extensions`.
  - `schemas/`: automated scan found 424 files containing `extensions`.
- Current interpreted extension usage is already substantial.
  - Automated runtime/tool scan found 81 Python files with direct `extensions.get(...)` reads.
  - The same scan found 368 literal interpretation sites spanning 238 unique extension keys.
- Existing interpreted keys are mostly bare legacy keys, not namespaced keys.
- Existing data and registry payloads also contain many bare extension keys.
- Shared ingress points previously loaded JSON without extension normalization in:
  - `tools/xstack/compatx/canonical_json.py`
  - `tools/xstack/compatx/schema_registry.py`
  - `tools/xstack/sessionx/common.py`
  - `tools/distribution/distribution_lib.py`
  - `tools/xstack/pack_loader/loader.py`
  - `src/geo/overlay/overlay_merge_engine.py`
  - `src/geo/worldgen/worldgen_engine.py`

## Implicit Interpretation Hotspots
- Worldgen:
  - `src/worldgen/mw/mw_cell_generator.py`
  - `src/worldgen/mw/system_query_engine.py`
  - `src/worldgen/earth/climate_field_engine.py`
  - `src/worldgen/earth/hydrology_engine.py`
  - `src/worldgen/earth/tide_field_engine.py`
  - `src/worldgen/earth/water/water_view_engine.py`
  - `src/worldgen/earth/wind/wind_field_engine.py`
- Client and renderer:
  - `src/client/interaction/affordance_generator.py`
  - `src/client/interaction/interaction_dispatch.py`
  - `src/client/render/renderers/software_renderer.py`
  - `src/client/render/renderers/null_renderer.py`
- Session/runtime tooling:
  - `tools/xstack/sessionx/creator.py`
  - `tools/xstack/sessionx/runner.py`
  - `tools/xstack/sessionx/process_runtime.py`

## Platform Assumptions And Risks
- Pre-task loaders normalized JSON object ordering only through generic JSON sorting at hash time.
- Pre-task extension interpretation was not backed by a central registry.
- Pre-task bare keys created cross-platform and mod-compatibility risk because parser behavior and interpretation discipline were implicit.

## Task Direction
- Preserve compatibility for existing bare keys in default mode.
- Add namespaced registry aliases for current interpreted keys.
- Normalize extensions before hashing and validation.
- Add strict/warn/refuse policy surface without changing simulation semantics.
