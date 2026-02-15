Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Canon-aligned with `docs/canon/constitution_v1.md` and `tools/xstack/compatx/version_registry.json`.

# Canonical Schemas Directory

## Purpose
Host canonical JSON Schema contracts (`v1.0.0`) used by XStack CompatX validation tooling.

## Invariants
- Schemas in this directory are strict top-level contracts with explicit required fields.
- Payloads are validated deterministically by `tools/xstack/compatx/validator.py`.
- Unknown top-level fields, missing required fields, and version mismatches are refused.
- Every schema declares `version: "1.0.0"` and requires payload `schema_version: "1.0.0"`.

## Canonical Files
- `schemas/universe_identity.schema.json`
- `schemas/universe_state.schema.json`
- `schemas/session_spec.schema.json`
- `schemas/authority_context.schema.json`
- `schemas/law_profile.schema.json`
- `schemas/lens.schema.json`
- `schemas/bundle_profile.schema.json`
- `schemas/pack_manifest.schema.json`
- `schemas/bundle_lockfile.schema.json`
- `schemas/registry_outputs.schema.json`
- `schemas/domain_registry.schema.json`
- `schemas/law_registry.schema.json`
- `schemas/experience_registry.schema.json`
- `schemas/lens_registry.schema.json`
- `schemas/astronomy_catalog_index.schema.json`
- `schemas/ui_registry.schema.json`

Examples are provided under `schemas/examples/*.example.json`.

## TODO
- Add migration route implementations once post-`1.0.0` versions are introduced.
- Add signed schema bundle export path for release packaging.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/contracts/versioning_and_migration.md`
- `tools/xstack/compatx/version_registry.json`
