Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Canon-aligned with `docs/canon/constitution_v1.md` and `tools/xstack/compatx/version_registry.json`.

# Former Root Schemas Directory

This file was preserved from the retired root-level `schemas/` directory during CONVERGE-06. The active schema root is now `contracts/schema/`.

## Purpose
Host canonical JSON Schema contracts (`v1.0.0`) used by XStack CompatX validation tooling.

## Invariants
- Schemas in this directory are strict top-level contracts with explicit required fields.
- Payloads are validated deterministically by `tools/xstack/compatx/validator.py`.
- Unknown top-level fields, missing required fields, and version mismatches are refused.
- Every schema declares `version: "1.0.0"` and requires payload `schema_version: "1.0.0"`.

## Canonical Files
- `contracts/schema/universe_identity.schema.json`
- `contracts/schema/universe_state.schema.json`
- `contracts/schema/session_spec.schema.json`
- `contracts/schema/authority_context.schema.json`
- `contracts/schema/law_profile.schema.json`
- `contracts/schema/lens.schema.json`
- `contracts/schema/bundle_profile.schema.json`
- `contracts/schema/pack_manifest.schema.json`
- `contracts/schema/bundle_lockfile.schema.json`
- `contracts/schema/registry_outputs.schema.json`
- `contracts/schema/domain_registry.schema.json`
- `contracts/schema/law_registry.schema.json`
- `contracts/schema/experience_registry.schema.json`
- `contracts/schema/lens_registry.schema.json`
- `contracts/schema/astronomy_catalog_index.schema.json`
- `contracts/schema/ui_registry.schema.json`

Examples are provided under `contracts/schema/examples/*.example.json`.

## TODO
- Add migration route implementations once post-`1.0.0` versions are introduced.
- Add signed schema bundle export path for release packaging.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/contracts/versioning_and_migration.md`
- `tools/xstack/compatx/version_registry.json`
