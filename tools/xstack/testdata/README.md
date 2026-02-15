Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0 and `docs/testing/xstack_profiles.md`.

# XStack Test Fixtures

## Purpose
Provide deterministic fixtures for TestX tool tests without relying on OS file ordering.

## Fixture Roots
- `tools/xstack/testdata/packs/`: fixture pack manifests and contribution payloads.
- `tools/xstack/testdata/bundles/`: fixture BundleProfile manifests for fixture packs.
- `tools/xstack/testdata/session/`: session creator/boot fixture inputs and schema-valid sample files.
  - includes camera/time intent scripts and restrictive law fixtures for process-gating tests.

## Invariants
- Fixtures are canonical JSON and deterministic.
- Bundle fixture IDs must match fixture pack IDs.
- No executable code is allowed in fixture pack content.

## Cross-References
- `docs/testing/xstack_profiles.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/pack_system.md`
