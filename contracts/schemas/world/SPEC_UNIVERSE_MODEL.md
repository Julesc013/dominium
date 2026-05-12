--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- IDs, coordinate frames, ACT time, deterministic scheduling primitives.
GAME:
- Interprets world data into gameplay effects and binds to CIV/WAR/INF systems.
SCHEMA:
- Universe data formats, versioning, and validation rules.
TOOLS:
- Future editors/importers/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic or mechanics in schema specs.
- No hard-coded Sol/Earth special cases.
- No per-tick world simulation or floating-point time dependence.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_UNIVERSE_MODEL - Universe Model (CONTENT0)

Status: draft
Version: 1

## Purpose
Define the top-level Universe data model and root references for galaxies and
systems as data only.

## UniverseRecord schema
Required fields:
- universe_id
- name
- coordinate_frame_ref
- time_standard_ref
- scale_domain_ref (universal)
- galaxy_ids (bounded list)
- provenance_ref
- metadata_tags (bounded list)

Rules:
- Universe has no parent; it is the root of the hierarchy.
- galaxy_ids ordering is deterministic and stable.
- coordinate_frame_ref and time_standard_ref reference existing frame/time specs.
- metadata_tags are descriptive only; no mechanics implied.

## UniverseCatalog schema
Required fields:
- catalog_id
- universe_ids (bounded list)
- default_universe_id
- provenance_ref

Rules:
- default_universe_id must appear in universe_ids.
- Catalogs are data-only and never imply player knowledge.

## Determinism and performance rules
- Universe data does not schedule updates and does not imply ticking.
- No global loads are required; access is interest-driven only.
- Any temporal changes must be represented as explicit data revisions or
  game-scheduled events, not schema logic.

## Epistemic rules
- Existence of data is not equivalent to player knowledge.
- Discovery and visibility must flow through sensors and reports.

## Validation rules
- universe_id and catalog_id are stable, unique, and immutable.
- No circular references (Universe cannot be its own descendant).
- Lists are schema-bounded with explicit max sizes.

## Integration points
- Reference frames: `docs/SPEC_REFERENCE_FRAMES.md`
- Time standards: `docs/SPEC_TIME_STANDARDS.md`
- Scale domains: `schema/scale/SPEC_SCALE_DOMAINS.md`
- Interest sets: `docs/SPEC_INTEREST_SETS.md`

## Prohibitions
- No gameplay logic embedded in universe data.
- No per-tick updates implied by data.
- No floating-point time dependence.

## Test plan (spec-level)
Required scenarios:
- Structural validation: unique IDs, bounded lists, and valid references.
- Migration: MAJOR version bump requires explicit migration or refusal.
- Determinism: identical inputs produce identical catalogs and ordering.
- Performance: interest-driven loading; no global iteration over galaxies.
