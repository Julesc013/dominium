Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0, `docs/canon/glossary_v1.md` v1.0.0, and lockfile schema `schemas/bundle_lockfile.schema.json` v1.0.0.

# Deterministic Packaging v1

## Purpose
Define canonical packaging from compiled bundle artifacts into a reproducible `dist` layout for Lab Galaxy validation.

## Canonical Dist Layout
Root:
- `dist/bin/`
- `dist/packs/`
- `dist/bundles/<bundle_id>/bundle.json`
- `dist/registries/`
- `dist/lockfile.json`
- `dist/manifest.json`

Expected registry files in `dist/registries/`:
- `domain.registry.json`
- `law.registry.json`
- `experience.registry.json`
- `lens.registry.json`
- `activation_policy.registry.json`
- `budget_policy.registry.json`
- `fidelity_policy.registry.json`
- `astronomy.catalog.index.json`
- `site.registry.index.json`
- `ui.registry.json`

## Build Entry
- `tools/setup/build --bundle bundle.base.lab --out dist`
- Implementation: `tools/setup/build.py`
- Internal engine: `tools/xstack/packagingx/dist_build.py`

## Deterministic Rules
1. Compile input registries + lockfile via existing XStack registry compile pipeline.
2. Copy resolved packs only, using deterministic path ordering.
3. Canonical-write JSON artifacts (`bundle.json`, registries, `lockfile.json`, `manifest.json`).
4. Normalize text launcher/setup stubs with `\n` newlines.
5. Remove managed dist subtrees before rebuild:
   - `bin/`, `packs/`, `bundles/`, `registries/`, `lockfile.json`, `manifest.json`
6. Never include file timestamps or OS metadata in canonical hashes.

## Manifest Contract
`dist/manifest.json` fields include:
- `schema_version: "1.0.0"`
- `manifest_type: "dominium.dist_manifest"`
- `layout_version: "1.0.0"`
- `bundle_id`
- version fields (`build_version`, `engine_version`, `client_version`, `server_version`, `setup_version`, `launcher_version`)
- `compatibility_version`
- `pack_lock_hash`
- `registry_hashes`
- `registry_hash_chain`
- `composite_hash_anchor_baseline`
- `resolved_packs[]`
- `managed_file_count`
- `file_hashes[]`
- `canonical_content_hash`

`canonical_content_hash` is the canonical hash of managed dist files excluding `manifest.json` to avoid self-reference cycles.

## Refusal Cases
- `REFUSE_DIST_COMPILE_FAILED`
- `REFUSE_DIST_BUNDLE_INVALID`
- `REFUSE_DIST_PACK_MISSING`
- `REFUSE_DIST_REGISTRY_MISSING`
- `REFUSE_DIST_REGISTRY_HASH_MISMATCH`
- `REFUSE_DIST_MANIFEST_INVALID`
- `REFUSE_DIST_CONTENT_HASH_MISMATCH`

Launcher-facing compatibility refusals:
- `LOCKFILE_MISMATCH`
- `PACK_INCOMPATIBLE`
- `REGISTRY_MISMATCH`

## Reproducibility Check
Strict validation builds dist twice and verifies:
1. identical `canonical_content_hash`
2. identical `manifest_hash`
3. identical `pack_lock_hash`
4. identical registry hash map

If binary payloads are not bundled in this repository checkout, deterministic guarantees still hold for canonical content hashes across JSON/config/pack artifacts.

## Example
```text
tools/setup/build --bundle bundle.base.lab --out dist
tools/launcher/launch run --dist dist --session saves/save.demo/session_spec.json
```

## TODO
- Add optional detached signature manifest after SecureX signing workflow is finalized.
- Introduce explicit schema for `dist/manifest.json` in CompatX when packaging contract stabilizes.

## Cross-References
- `docs/architecture/registry_compile.md`
- `docs/architecture/lockfile.md`
- `docs/architecture/setup_and_launcher.md`
- `docs/contracts/refusal_contract.md`
- `docs/testing/xstack_profiles.md`
