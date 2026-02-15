Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/bundle_profile.schema.json` v1.0.0 and `docs/architecture/pack_system.md`.

# Bundle Profiles

## Purpose
Store declarative bundle selections under `bundles/<bundle_id>/bundle.json` for deterministic lockfile and registry compile.

## Invariants
- Bundle files validate against `schemas/bundle_profile.schema.json`.
- `pack_ids` order is not trusted for dependency ordering.
- Dependency order is resolved by `tools/xstack/pack_loader/dependency_resolver.py`.
- Runtime must consume compiled registries + lockfile; no ad hoc bundle merge at boot.

## Commands
- `tools/xstack/bundle_list`
- `tools/xstack/bundle_validate bundles/bundle.base.lab/bundle.json`
- `tools/xstack/lockfile_build --bundle bundle.base.lab --out build/lockfile.json`

## Cross-References
- `docs/architecture/pack_system.md`
- `docs/architecture/session_lifecycle.md`
- `docs/contracts/versioning_and_migration.md`
