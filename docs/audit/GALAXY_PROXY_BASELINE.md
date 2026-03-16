Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GAL-0 Galaxy Proxy Baseline

Date: 2026-03-13
Status: GAL-0 scoped pass

## Field Definitions

- `field.stellar_density_proxy`
  - scalar permille proxy
  - canonical value source: shared MW density derivation
- `field.metallicity_proxy`
  - scalar permille proxy
  - canonical value source: shared MW radial metallicity gradient
- `field.radiation_background_proxy`
  - scalar permille proxy
  - canonical value source: GAL-0 center/height/density stub
- `field.galactic_region_id`
  - scalar enum code
  - registry: `data/registries/galactic_region_registry.json`

## Derivation Rules

For each galaxy cell in `geo.topology.r3_infinite` / `geo.partition.grid_zd`:

- position:
  - `x_pc, y_pc, z_pc = mw_cell_position_pc(cell_key, cell_size_pc)`
- radius:
  - `R = sqrt(x_pc^2 + y_pc^2)` using integer `isqrt`
- stellar density:
  - `stellar_density_proxy = mw_density_permille(...)`
- metallicity:
  - `metallicity_proxy = mw_metallicity_permille(priors_row, R)`
- region:
  - `bulge` if bulge distance is within `bulge_radius`
  - `halo` if `|z|` exceeds `2 * disk_half_thickness` or `R > disk_radius`
  - `inner_disk` if `R <= max(bulge_radius + 1, disk_radius / 2)`
  - otherwise `outer_disk`
- radiation:
  - center term weighted toward low `R`
  - vertical term weighted toward low `|z|`
  - density term weighted from `stellar_density_proxy`
  - bulge floor `760`, halo cap `240`

All outputs are integer, clamped, and ordered by canonical `geo_cell_key`.

## Stability Markers

All GAL-0 proxy rows are `provisional`.

- `future_series`: `GAL+/ASTRO`
- `replacement_target`: `dynamic galaxy domain packs`

Covered surfaces:

- field type rows
- field binding rows
- galactic region registry rows

## Locked Hashes

- combined replay hash: `e5aff9a414dbe2e713e5a4def71039de453a77cdbc6aa3fa858304fe31162616`
- proxy window hash: `a4d31890a367986fe701fb36b2f90db367408cbd00b85cf78a7a57edbe74db55`
- field projection hash: `8b4e3ea724e36f726b10b9ed28e6202c8ed720dd46e9d21719719951d811baa7`
- process field update hash chain: `dc735e2cd0ba1cc2e7bced542393a03413ebd33347badff7631ebb7aff213450`
- update plan fingerprint: `9904c91819487d9fd5e0410b9e0b7e42bc181308d88a22487519e0229a6e8bda`

## Validation Summary

- replay tool:
  - `tools/worldgen/tool_replay_galaxy_proxies.py` -> pass
- TestX:
  - `test_galaxy_proxy_fields_deterministic` -> pass
  - `test_region_id_thresholds_stable` -> pass
  - `test_cross_platform_galaxy_proxy_hash_match` -> pass
- RepoX scoped GAL-0 invariant hook:
  - `0` findings
- AuditX scoped GAL-0 analyzers:
  - `E463_UNTAGGED_STUB_SMELL` -> `0`
  - `E464_CATALOG_DEPENDENCY_SMELL` -> `0`

## Full-Lane Note

Full-repo `RepoX STRICT` still refuses on unrelated pre-existing repository debt.

Full `AuditX` scan and `tools/xstack/run.py strict` both timed out in the local validation window, so this report records scoped GAL-0 readiness, not a repository-wide strict green state.

## Readiness

GAL-0 is ready for:

- `GAL-1` compact object stubs
- `META-STABILITY-1` tagging sweep

The proxy layer remains additive-only, deterministic, catalog-free, and explicitly provisional.
