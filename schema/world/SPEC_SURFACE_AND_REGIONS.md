--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- IDs, coordinate frames, ACT time, deterministic scheduling primitives.
GAME:
- Interprets surfaces and regions for governance, logistics, war, and ecology.
SCHEMA:
- Surface, region, and volume formats, versioning, and validation rules.
TOOLS:
- Future editors/importers/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic or mechanics in schema specs.
- No per-tick world simulation or grid assumptions.
- No hard-coded Sol/Earth special cases.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_SURFACE_AND_REGIONS - Surfaces, Regions, and Volumes (CONTENT0)

Status: draft
Version: 1

## Purpose
Define deterministic surface, region, and volume data used for governance and
logistics without embedding mechanics.

## SurfaceRecord schema
Required fields:
- surface_id
- body_ref
- surface_type (land/ocean/ice/gas)
- coordinate_frame_ref
- heightmap_ref
- climate_map_ref
- biome_tags (bounded list)
- region_ids (bounded list)
- provenance_ref

Optional fields:
- surface_tags (bounded list)
- coverage_bounds_ref

Rules:
- Surfaces are data layers only; no simulation implied.
- region_ids ordering is deterministic and stable.

## RegionRecord schema
Required fields:
- region_id
- surface_ref (nullable)
- volume_ref (nullable)
- boundary_ref
- region_type (administrative/natural/logistics/war)
- parent_region_ref (nullable)
- layer_id
- region_tags (bounded list)
- provenance_ref

Rules:
- Each region belongs to exactly one surface or volume.
- boundary_ref references explicit geometry; no fixed grid requirement.
- Overlap is allowed only within the same layer_id with explicit stacking rules.

## VolumeRecord schema
Required fields:
- volume_id
- body_ref
- volume_type (underground/ocean_layer/atmosphere_layer/orbital_shell)
- coordinate_frame_ref
- bounds_ref
- region_ids (bounded list)
- provenance_ref

Rules:
- Volumes are data only; no simulation implied.
- region_ids ordering is deterministic and stable.

## Determinism and performance rules
- All lists are bounded and deterministically ordered.
- Data does not imply ticking or global iteration.
- Loading is interest-driven; no global surface scans required.

## Epistemic rules
- Surface and region data existence does not grant knowledge.
- Discovery and visibility must flow through sensors and reports.

## Validation rules
- surface_id, region_id, and volume_id are stable and unique.
- parent_region_ref must not form cycles.
- Lists are schema-bounded with explicit max sizes.

## Integration points
- Celestial bodies: `schema/world/SPEC_CELESTIAL_BODY.md`
- Governance: `schema/governance/SPEC_JURISDICTIONS.md`
- Logistics: `schema/civ/SPEC_LOGISTICS_FLOWS.md`
- War domains: `schema/war/SPEC_CONFLICT_CANON.md`

## Prohibitions
- No gameplay logic embedded in surface or region data.
- No per-tick updates or fixed grid assumptions.
- No special-case Sol/Earth logic.

## Test plan (spec-level)
Required scenarios:
- Structural validation: unique IDs, bounded lists, and valid references.
- Migration: MAJOR version bump requires explicit migration or refusal.
- Determinism: identical inputs produce identical region orderings.
- Performance: interest-driven loading; no global region scans.
