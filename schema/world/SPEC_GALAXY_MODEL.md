--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- IDs, coordinate frames, ACT time, deterministic scheduling primitives.
GAME:
- Interprets world data into gameplay effects and binds to CIV/WAR/INF systems.
SCHEMA:
- Galaxy data formats, versioning, and validation rules.
TOOLS:
- Future editors/importers/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic or mechanics in schema specs.
- No hard-coded Milky Way special cases.
- No physics simulation or per-tick world updates.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_GALAXY_MODEL - Galaxy Model (CONTENT0)

Status: draft
Version: 1

## Purpose
Define galaxy records and their deterministic linkage to star systems.

## GalaxyRecord schema
Required fields:
- galaxy_id
- universe_ref
- name
- coordinate_frame_ref
- scale_domain_ref (galactic)
- system_ids (bounded list)
- morphology_tags (bounded list)
- provenance_ref
- data_source_refs (bounded list)

Optional fields:
- procedural_fill_ref
- bounds_ref

Rules:
- universe_ref must reference a valid UniverseRecord.
- system_ids must reference StarSystem records within the same galaxy.
- morphology_tags use a controlled vocabulary; no gameplay effects implied.
- procedural_fill_ref must resolve to explicit seeds and policies.

## Determinism and performance rules
- system_ids ordering is deterministic and stable.
- No global iteration across all systems for a galaxy; access is interest-driven.
- Procedural fill must be reproducible from explicit seeds and inputs.

## Epistemic rules
- Existence of a galaxy record does not grant knowledge to any actor.
- Discovery and visibility must flow through sensors and reports.

## Validation rules
- galaxy_id is stable, unique, and immutable.
- No circular references between galaxies and systems.
- Lists are schema-bounded with explicit max sizes.

## Integration points
- Universe model: `schema/world/SPEC_UNIVERSE_MODEL.md`
- Scale domains: `schema/scale/SPEC_SCALE_DOMAINS.md`
- World data import: `schema/world/SPEC_WORLD_DATA_IMPORT.md`

## Prohibitions
- No gameplay logic embedded in galaxy data.
- No physics simulation or per-tick updates.
- No hard-coded Milky Way or Sol special cases.

## Test plan (spec-level)
Required scenarios:
- Structural validation: unique IDs, bounded lists, and valid references.
- Migration: MAJOR version bump requires explicit migration or refusal.
- Determinism: identical inputs produce identical system ordering.
- Performance: interest-driven loading; no global system scans.
