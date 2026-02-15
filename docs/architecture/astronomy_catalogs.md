Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0, `schemas/astronomy_catalog_entry.schema.json` v1.0.0, and `schemas/reference_frame.schema.json` v1.0.0.

# Astronomy Catalogs v1

## Purpose
Define pack-driven astronomy object and frame data contracts used by deterministic registry compile and teleport resolution.

## Canonical Schemas
- `schemas/astronomy_catalog_entry.schema.json` (`version: 1.0.0`)
- `schemas/reference_frame.schema.json` (`version: 1.0.0`)
- Derived output: `schemas/astronomy_catalog_index.schema.json` (`version: 1.0.0`)

## Object ID Policy
- IDs are stable, dot-delimited tokens: `object.<scope>.<name>`
- IDs are canonical content identity and must not be repurposed.
- Pack ownership is explicit by `pack_id` in source entry payload.
- If a later pack supersedes detail for an existing ID, precedence must remain deterministic and documented.

Example IDs:
- `object.milky_way`
- `object.sol_system`
- `object.sol`
- `object.earth`
- `object.luna`

## Hierarchy Contract
`parent_id` establishes deterministic hierarchy:
- `null` for top-level roots
- child entries must reference stable parent IDs
- hierarchy is data-declared, never inferred from file order

Example:
`object.sol_system` -> parent `object.milky_way.arm.orion`
`object.earth` -> parent `object.sol_system`
`object.luna` -> parent `object.earth`

## Reference Frame Contract
Frames are data-driven:
- `frame_id`
- `parent_frame_id` (`null` allowed)
- deterministic transform payload (`translation_mm`, `rotation_mdeg`)
- `semantics`: `galactic|system|body_fixed|orbital|local`

Frame transforms are deterministic representation records, not runtime solver outputs in this phase.

## Deterministic Search Rules
Search keys compile into `astronomy.catalog.index.json.search_index` using deterministic normalization:
1. lowercase
2. trim
3. collapse internal whitespace
4. Unicode normalize (NFKD) then remove non-ASCII

Search map value ordering is deterministic:
- sorted unique `object_id[]`

## Refusal Cases
- contribution payload missing `entry_type`
- malformed `entries[]` or `frames[]`
- schema validation failure for object/frame rows
- pack_id mismatch between contribution owner and row payload

## Extension (Pack-Only)
To add a new body via a mod pack:
1. Add pack under `packs/domain/<pack_id>/`.
2. Add `pack.json` with `registry_entries` contributions.
3. Add one or more files with:
   - `entry_type: astronomy_catalog_collection`
   - `entry_type: reference_frame_collection`
4. Validate with:
   - `tools/xstack/bundle_validate bundles/bundle.base.lab/bundle.json`
   - `tools/xstack/registry_compile --bundle bundle.base.lab`
5. Verify index content:
   - `build/registries/astronomy.catalog.index.json`

No runtime engine/client edits are required for catalog extension.

## Stability and CompatX
- Schema versioning is managed via `tools/xstack/compatx/version_registry.json`.
- Breaking schema changes require explicit migration or deterministic refusal.
- Stable IDs should be treated as compatibility contracts across pack versions.

## TODO
- Add deterministic duplicate-ID policy for multi-pack overrides.
- Add optional orbital parameter precision profile guidance.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/site_registry.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/camera_and_navigation.md`
