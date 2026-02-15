Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `tools/xstack/compatx/version_registry.json` and canonical schemas `schemas/*.schema.json`.

# Versioning And Migration Contract

## Purpose
Define deterministic schema-version handling and explicit CompatX migration behavior for canonical `v1.0.0` contracts.

## Source of Truth
- Registry: `tools/xstack/compatx/version_registry.json`
- Validator: `tools/xstack/compatx/validator.py`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## Forward Compatibility Policy
- Payloads with `schema_version == current_version` validate normally.
- Payloads with unknown `schema_version` are refused deterministically.
- No silent coercion, implicit defaulting, or best-effort field guessing is allowed.

## Backward Compatibility Policy
- If `schema_version` is listed in `supported_versions` and is lower than `current_version`, CompatX migration routing is invoked explicitly.
- In this phase, migration routing is a stub and returns deterministic refusal until migration implementations exist.
- Backward support is registry-declared, never inferred from ad hoc code.

## Refusal Behavior
- Missing `schema_version` -> `refuse.compatx.missing_payload_version`
- Unsupported `schema_version` -> `refuse.compatx.unsupported_schema_version`
- Migration route invoked but not implemented -> `refuse.compatx.migration_not_implemented`
- Unknown top-level fields -> `unknown_top_level_field`

## Schema Bump Process
1. Bump schema file `version` in `schemas/<name>.schema.json`.
2. Update `tools/xstack/compatx/version_registry.json` with new `current_version`.
3. Add previous versions to `supported_versions` only when explicit migration/refusal behavior is declared.
4. Implement migration route or keep deterministic refusal path.
5. Update contract docs and examples to the new version.
6. Re-run `tools/xstack/run fast` and strict profile checks.

## Version Registry Example
```json
{
  "schemas": {
    "bundle_profile": {
      "current_version": "1.0.0",
      "supported_versions": [
        "1.0.0"
      ],
      "migrations": {}
    },
    "session_spec": {
      "current_version": "1.0.0",
      "supported_versions": [
        "1.0.0"
      ],
      "migrations": {}
    }
  }
}
```

## TODO
- Add concrete migration route declarations once `2.x` schemas are introduced.
- Add signed migration provenance records for audit packaging.
- Add compatibility matrix projection to `registry_outputs` once registry compile is implemented.

## Cross-References
- `docs/contracts/session_spec.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/law_profile.md`
- `docs/contracts/lens_contract.md`
- `schemas/bundle_profile.schema.json`
- `tools/xstack/compatx/version_registry.json`
