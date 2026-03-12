# GAL0 Retro Audit

Date: 2026-03-13
Scope: MW-0..3, GEO-4 field binding, EARTH sky/starfield derived view path

## Existing Galaxy Inputs

- `data/registries/galaxy_priors_registry.json` already carries the deterministic MW priors required for a proxy layer.
- `src/worldgen/mw/mw_cell_generator.py` already derives canonical per-cell values:
  - `galactocentric_position_pc`
  - `galactocentric_radius_pc`
  - `density_permille`
  - `metallicity_permille`
  - `habitable_filter_bias_permille`
- `generate_mw_cell_payload(...)` exposes those values through `mw_cell_summary` in the worldgen result.

## Existing Field Binding Surface

- `data/registries/field_binding_registry.json` already binds canonical scalar fields to galaxy cells under:
  - `topology_profile_id: geo.topology.r3_infinite`
  - `partition_profile_id: geo.partition.grid_zd`
  - `storage_kind: cell`
- The same registry already uses additive, non-breaking sibling `stability` markers for newer proxy fields.

## Existing Visual Dependence on Galaxy Priors

- `src/worldgen/earth/sky/starfield_generator.py` reads `galaxy_priors_rows()` directly.
- The Milky Way band brightness currently depends on:
  - spiral arm count
  - arm contrast
  - policy-driven band width and brightness
- No canonical galaxy proxy fields exist yet, so there is no field-backed alignment point for later starfield tuning.

## Existing Proxy/Replay Patterns

- `src/worldgen/earth/material/material_proxy_engine.py` provides the closest implementation template:
  - registry-backed scalar coding
  - deterministic evaluation
  - `process.field_update`-compatible field update rows
  - stable window hashing
- `tools/worldgen/earth10_probe.py` and `tools/worldgen/tool_replay_material_proxy_window.py` establish the preferred replay/test shape:
  - generate deterministic fixture window
  - apply updates through process runtime
  - compare overlay hash, field projection hash, and replay stability

## Safest Insertion Point

- Additive field types in `data/registries/field_type_registry.json`
- Additive galaxy-region registry in `data/registries/galactic_region_registry.json`
- Additive `field_binding_registry.json` rows for `geo.topology.r3_infinite` galaxy cells
- A deterministic proxy engine under `src/worldgen/galaxy/`
- Optional derived-view consumers only; no presentation state enters truth

## Risk Notes

- Reusing MW cell formulas is safer than inventing a second approximation path.
- Galaxy proxy fields must remain explicitly provisional:
  - future_series: `GAL+/ASTRO`
  - replacement_target: dynamic galaxy domain packs
- No external catalog inputs are present in current MW generation; GAL-0 must preserve that.
