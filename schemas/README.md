Status: DRAFT
Version: 1.0.0-draft
Last Reviewed: 2026-02-14
Compatibility: Canon-aligned with `docs/canon/constitution_v1.md` and schema law in `schema/`.

# Schemas Directory Placeholder

## Purpose
Reserve `schemas/` for future generated, composed, or exported schema artifacts that are distinct from source-of-truth schema definitions under `schema/`.

## Invariants
- Source-of-truth schema definitions remain under `schema/`.
- Any artifact placed in `schemas/` must declare provenance and source schema IDs.
- Generated schema artifacts must not silently diverge from source schema versions.

## Example Intended Usage
- Compiled schema bundles for tooling distribution.
- Snapshot exports of resolved contract sets per release.

## TODO
- Define naming convention for generated schema bundles.
- Add validation command contract for generated artifacts.

## Cross-References
- `docs/canon/constitution_v1.md`
- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_MIGRATION.md`

