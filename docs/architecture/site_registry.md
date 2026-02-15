Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0, `schemas/site_entry.schema.json` v1.0.0, and `schemas/site_registry_index.schema.json` v1.0.0.

# Site Registry v1

## Purpose
Define deterministic site records for on/above/within-body navigation targets resolved by `process.camera_teleport`.

## Canonical Schemas
- `schemas/site_entry.schema.json` (`version: 1.0.0`)
- Derived output: `schemas/site_registry_index.schema.json` (`version: 1.0.0`)

## Site ID Policy
- IDs are stable, dot-delimited: `site.<object_scope>.<site_name>`
- IDs are canonical and must not be reused for unrelated locations.
- Sites bind to owning body through `object_id`.

Example IDs:
- `site.earth.greenwich`
- `site.earth.low_earth_orbit_reference`
- `site.earth.earth_core_center`

## Site Kind and Position
Kinds (`v1`):
- `surface`
- `orbit`
- `interior`
- `atmosphere`
- `l4`
- `l5`
- `custom`

Position representations:
- `local_xyz_mm`
- `lat_lon_alt` (`lat_deg_x1e6`, `lon_deg_x1e6`, `alt_mm`)

Teleport resolution uses compiled index data only:
- no raw pack file reads at process execution time
- no non-deterministic lookup heuristics

## Deterministic Search Rules
`site.registry.index.json.search_index` uses the same normalization as astronomy:
1. lowercase
2. trim
3. collapse internal whitespace
4. Unicode normalize (NFKD) and strip non-ASCII

Search map values are deterministic:
- sorted unique `site_id[]`

## Refusal Cases
- `REGISTRY_MISSING` when compiled site registry is unavailable
- `TARGET_NOT_FOUND` when requested `target_site_id` is absent
- `PROCESS_INPUT_INVALID` when site position representation is invalid

`TARGET_AMBIGUOUS` is reserved for future name-query resolution paths (ID-based teleport is unambiguous).

## Extension (Pack-Only)
To add new sites in a pack:
1. Add/extend `registry_entries` contribution with `entry_type: site_collection`.
2. Provide schema-valid `sites[]` rows in JSON.
3. Recompile registries:
   - `tools/xstack/registry_compile --bundle bundle.base.lab`
4. Validate deterministic indices:
   - `build/registries/site.registry.index.json`
   - `tools/xstack/run fast`

No runtime branching or mode flags are required.

## Compatibility and Stability
- Site schema evolution follows CompatX (`tools/xstack/compatx/version_registry.json`).
- Stable `site_id` values are compatibility anchors for scripted navigation and tests.
- Breaking changes require migration or deterministic refusal.

## TODO
- Add optional site orientation hints for future camera facing defaults.
- Add index-level duplicate site ownership diagnostics.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/astronomy_catalogs.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/camera_and_navigation.md`
