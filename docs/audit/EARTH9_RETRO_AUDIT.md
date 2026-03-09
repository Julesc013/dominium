Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EARTH-9 Retro Audit

## Audit Targets

- remaining direct Truth reads in Earth view and render paths
- deterministic cache inputs across sky, illumination, water, and map views
- bounded-update guarantees for climate, tide, wind, hydrology, and shadow sampling
- existing proof/replay helpers that EARTH-9 can compose without adding new runtime features

## Findings

### Earth view paths remain derived-artifact-first

- `src/client/ui/viewer_shell.py` builds:
  - `sky_view_surface`
  - `illumination_view_surface`
  - `water_view_surface`
  - `map_views`
- `src/client/render/render_model_adapter.py` and `src/client/render/renderers/software_renderer.py` consume derived artifacts, not `truth_model` or `universe_state`.
- `src/client/ui/map_views.py` keys view caches by `truth_hash_anchor`, lens inputs, and layer-source hashes.
- Conclusion:
  - no new view/runtime truth bridge is needed for EARTH-9.

### Existing Earth update engines are already bounded and degrade explicitly

- `src/worldgen/earth/climate_field_engine.py`, `src/worldgen/earth/tide_field_engine.py`, and `src/worldgen/earth/wind/wind_field_engine.py` already expose:
  - deterministic bucket scheduling
  - `max_tiles_per_update`
  - `degraded`
  - `degrade_reason`
- `src/worldgen/earth/lighting/horizon_shadow_engine.py` already uses fixed sample counts.
- `src/worldgen/earth/hydrology_engine.py` already supports bounded local recompute after geometry edits.
- Conclusion:
  - EARTH-9 should verify these bounded contracts, not add alternate update loops.

### Existing replay/probe tools already cover the Earth MVP subsystems

- Existing deterministic replay/probe helpers already exist for:
  - hydrology: `tools/worldgen/earth1_probe.py`
  - climate: `tools/worldgen/earth2_probe.py`
  - tide: `tools/worldgen/earth3_probe.py`
  - sky: `tools/worldgen/earth4_probe.py`
  - illumination: `tools/worldgen/earth5_probe.py`
  - terrain collision: `tools/embodiment/earth6_probe.py`
  - wind: `tools/worldgen/earth7_probe.py`
  - water visuals: `tools/worldgen/earth8_probe.py`
- Conclusion:
  - EARTH-9 should compose these probes into a single deterministic stress envelope and regression lock.

### Fix List

- add one canonical EARTH-9 stress scenario generator and runner under `tools/earth/`
- add composed replay tools for Earth views and Earth movement windows
- add a regression lock artifact under `data/regression/earth_mvp_baseline.json`
- add RepoX/AuditX rules that enforce:
  - Earth views remain derived-only
  - Earth update loops stay bounded
  - Earth stress/replay surfaces stay deterministic
