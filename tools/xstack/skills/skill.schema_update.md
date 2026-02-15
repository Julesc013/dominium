Status: TEMPLATE
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Use with schema law (`schema/SCHEMA_VERSIONING.md`, `schema/SCHEMA_MIGRATION.md`) and canon v1.0.0.

# Skill Template: schema_update

## Purpose
Apply schema changes safely with explicit compatibility, migration/refusal, and test obligations.

## Constraints
- Do not change schema meaning without semver-accurate version bump.
- Do not silently coerce old data.
- Preserve unknown/open-map fields where required.
- Avoid adding schema fields "just in case" without a direct contract need.

## Checklist
1. Identify affected `schema_id` and current version.
2. Classify change: PATCH, MINOR, or MAJOR.
3. Update schema metadata fields (`schema_version`, `stability`) as needed.
4. Add/adjust migration route or explicit refusal behavior.
5. Update related docs under `docs/contracts/` and `docs/architecture/`.
6. Update compatibility notes (CompatX-facing docs) when behavior changes.
7. Run schema-focused tests and required gate profile.
   - `tools/xstack/schema_validate session_spec schemas/examples/session_spec.example.json`
   - `tools/xstack/schema_validate bundle_profile schemas/examples/bundle_profile.example.json`
   - `tools/xstack/run fast`
8. Record remaining TODOs clearly.

## Output Format
- Change classification and rationale.
- Files updated.
- Migration/refusal path summary.
- Validation run summary.

## Example Invocation
```text
Use skill.schema_update for schema/lens/lens.schema:
- Add a backward-compatible field.
- Keep extension preservation.
- Update contracts and run FAST validation.
Run:
- tools/xstack/schema_validate lens schemas/examples/lens.example.json
- tools/xstack/run strict
```

## TODO
- Add canned migration template snippets for MAJOR changes.
- Add deterministic diff checker for schema contract docs.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/contracts/lens_contract.md`
- `docs/governance/COMPATX_MODEL.md`
- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_MIGRATION.md`
