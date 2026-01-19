--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- IDs, coordinate frames, ACT time, deterministic scheduling primitives.
GAME:
- Interprets imported data through gameplay systems.
SCHEMA:
- Import manifest formats, versioning, and validation rules.
TOOLS:
- Importers and validators only (no runtime behavior).
FORBIDDEN:
- No runtime logic or mechanics in schema specs.
- No runtime guessing or implicit data synthesis.
- No floating-point time dependence.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_WORLD_DATA_IMPORT - World Data Import (CONTENT0)

Status: draft
Version: 1

## Purpose
Define deterministic import manifests and rules for real-world and procedural
world data without embedding mechanics.

## ImportSourceRecord schema
Required fields:
- source_id
- source_type (heightmap/climate/geology/catalog/ephemeris)
- source_version
- checksum
- license_ref
- provenance_ref

Optional fields:
- uri_ref
- attribution_ref

Rules:
- checksum is required to ensure reproducibility.
- license_ref and attribution_ref are required for external sources.

## ImportMappingRecord schema
Required fields:
- mapping_id
- source_ref
- target_schema_id
- target_entity_ref
- transform_ref
- merge_policy (override/augment)
- missing_data_policy (procedural_fill/explicit_null)
- provenance_ref

Rules:
- transform_ref defines deterministic coordinate transforms.
- missing_data_policy must be explicit; no runtime guessing is allowed.

## ImportManifest schema
Required fields:
- manifest_id
- source_ids (bounded list)
- mapping_ids (bounded list)
- output_universe_ref
- provenance_ref

Rules:
- Manifests are deterministic; same inputs produce the same outputs.
- Missing data is filled only by explicit procedural rules with fixed seeds.

## Determinism and performance rules
- Imports must be reproducible from versioned sources and checksums.
- Mapping application order is deterministic and stable.
- Lists are schema-bounded with explicit max sizes.

## Epistemic rules
- Imported data existence does not grant player knowledge.
- Knowledge must flow through sensors and reports.

## Validation rules
- source_id, mapping_id, and manifest_id are stable and unique.
- All referenced entities and schemas must exist and match versions.
- No circular mapping dependencies are allowed.

## Integration points
- Schema governance: `schema/SCHEMA_GOVERNANCE.md`
- Schema versioning: `schema/SCHEMA_VERSIONING.md`
- Universe model: `schema/world/SPEC_UNIVERSE_MODEL.md`

## Prohibitions
- No runtime guessing or implicit data synthesis.
- No per-tick updates implied by import data.
- No floating-point time dependence.

## Test plan (spec-level)
Required scenarios:
- Structural validation: unique IDs, bounded lists, and valid references.
- Migration: MAJOR version bump requires explicit migration or refusal.
- Determinism: identical sources and mappings produce identical outputs.
- Performance: bounded mappings; no global scans during import.
