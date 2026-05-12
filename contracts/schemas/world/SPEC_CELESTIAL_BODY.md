--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- IDs, coordinate frames, ACT time, deterministic scheduling primitives.
GAME:
- Interprets body data into gameplay effects and binds to CIV/WAR/INF systems.
SCHEMA:
- Celestial body formats, versioning, and validation rules.
TOOLS:
- Future editors/importers/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic or mechanics in schema specs.
- No physics simulation or per-tick world updates.
- No hard-coded Sol/Earth special cases.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_CELESTIAL_BODY - Celestial Bodies (CONTENT0)

Status: draft
Version: 1

## Purpose
Define deterministic records for stars, planets, moons, and related bodies as
data only.

## CelestialBodyRecord schema
Required fields:
- body_id
- system_ref
- parent_body_ref (nullable)
- body_type (star/planet/moon/dwarf/asteroid/belt/station/comet)
- name
- radius_m (integer meters)
- mass_class (tag)
- surface_refs (bounded list)
- volume_refs (bounded list)
- orbital_rail_ref (nullable)
- scale_domain_ref
- provenance_ref
- data_source_refs (bounded list)
- body_tags (bounded list)

Optional fields:
- rotation_period_act
- axial_tilt_mdeg
- atmosphere_ref

Rules:
- parent_body_ref is required for moons and optional for stations; stars have none.
- orbital_rail_ref is required for orbiting bodies and must reference an orbital rail.
- radius_m and rotation_period_act are integers; no floating-point time dependence.
- surface_refs and volume_refs are descriptive and do not imply simulation.

## Determinism and performance rules
- Body IDs and references are stable and deterministically ordered.
- No per-tick updates are implied by body data.
- Any temporal change is represented via explicit data revisions or game events.

## Epistemic rules
- Body data existence does not grant omniscient knowledge.
- Discovery and visibility must flow through sensors and reports.

## Validation rules
- body_id is stable, unique, and immutable.
- parent and system references must be consistent.
- Lists are schema-bounded with explicit max sizes.

## Integration points
- Star systems: `schema/world/SPEC_SYSTEM_MODEL.md`
- Orbital rails: `schema/world/SPEC_ORBITAL_RAILS.md`
- Surfaces and regions: `schema/world/SPEC_SURFACE_AND_REGIONS.md`
- Scale domains: `schema/scale/SPEC_SCALE_DOMAINS.md`

## Prohibitions
- No gameplay logic embedded in body data.
- No physics simulation or per-tick updates.
- No special-case Sol/Earth logic.

## Test plan (spec-level)
Required scenarios:
- Structural validation: unique IDs, bounded lists, and valid references.
- Migration: MAJOR version bump requires explicit migration or refusal.
- Determinism: identical inputs produce identical body catalogs.
- Performance: interest-driven loading; no global body scans.
