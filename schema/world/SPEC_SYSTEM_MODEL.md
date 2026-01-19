--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- IDs, coordinate frames, ACT time, deterministic scheduling primitives.
GAME:
- Interprets world data into gameplay effects and binds to CIV/WAR/INF systems.
SCHEMA:
- Star system data formats, versioning, and validation rules.
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
# SPEC_SYSTEM_MODEL - Star System Model (CONTENT0)

Status: draft
Version: 1

## Purpose
Define star system records and their deterministic linkage to celestial bodies
and orbital rails.

## StarSystemRecord schema
Required fields:
- system_id
- galaxy_ref
- name
- coordinate_frame_ref
- scale_domain_ref (system)
- star_ids (bounded list)
- planet_ids (bounded list)
- belt_ids (bounded list)
- orbital_rail_ids (bounded list)
- provenance_ref
- data_source_refs (bounded list)

Optional fields:
- route_node_ref
- procedural_fill_ref
- system_tags (bounded list)

Rules:
- galaxy_ref must reference a valid GalaxyRecord.
- star_ids, planet_ids, and belt_ids must reference valid CelestialBody records.
- orbital_rail_ids must reference rails within the same system.
- route_node_ref is a data hook for CIV4 graphs; no mechanics implied.
- procedural_fill_ref must resolve to explicit seeds and policies.

## Determinism and performance rules
- All body ID lists are deterministically ordered.
- No global iteration across all systems; access is interest-driven.
- System contents are data only and never imply ticking.

## Epistemic rules
- System data does not grant omniscient knowledge.
- Discovery and visibility must flow through sensors and reports.

## Validation rules
- system_id is stable, unique, and immutable.
- Parent references must match galaxy and universe hierarchies.
- Lists are schema-bounded with explicit max sizes.

## Integration points
- Galaxy model: `schema/world/SPEC_GALAXY_MODEL.md`
- Celestial bodies: `schema/world/SPEC_CELESTIAL_BODY.md`
- Orbital rails: `schema/world/SPEC_ORBITAL_RAILS.md`
- Scale domains: `schema/scale/SPEC_SCALE_DOMAINS.md`

## Prohibitions
- No gameplay logic embedded in system data.
- No physics simulation or per-tick updates.
- No special-case Sol/Earth logic.

## Test plan (spec-level)
Required scenarios:
- Structural validation: unique IDs, bounded lists, and valid references.
- Migration: MAJOR version bump requires explicit migration or refusal.
- Determinism: identical inputs produce identical system catalogs.
- Performance: interest-driven loading; no global system scans.
