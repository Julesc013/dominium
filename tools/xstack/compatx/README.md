Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# XStack CompatX Schema Substrate

## Purpose
Provide deterministic schema validation tooling for canonical `schemas/*.schema.json` contracts.

## Invariants
- Validation is strict: missing required fields, unknown top-level fields, and version mismatch refuse.
- Deterministic serialization uses UTF-8, stable key ordering, compact JSON, and no trailing whitespace.
- Version handling is registry-driven through `tools/xstack/compatx/version_registry.json`.
- Migration routing is explicit and deterministic; migration execution is currently a stub.

## CLI
- `tools/xstack/schema_validate <schema_name> <file_path>`
- `python tools/xstack/compatx/profile_checks.py --repo-root . --profile FAST`
- `tools/xstack/compatx/check --profile FAST`

## Scope Limits
- This substrate validates contracts only.
- No runtime simulation logic, engine mutation, renderer behavior, or registry compile behavior is implemented here.

## TODO
- Replace migration stub execution with declared route runner once migration specs exist.
- Add richer JSON Schema keyword support only when canonical contracts require it.
- Add signed schema bundle export path for release artifacts.

## Cross-References
- `docs/contracts/versioning_and_migration.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
