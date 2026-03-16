Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: release-pinned artifact manifest audit archive after RELEASE-2

# RELEASE-1 Retro Audit

## Scope

- Distribution root assumptions under `dist/`
- Existing install and artifact manifests under `schema/lib/*` and `schema/install.manifest.schema`
- Existing lockfile and pack-lock outputs under `dist/locks/` and `dist/lockfile.json`
- Existing build identity and descriptor emission under `src/release/build_id_engine.py` and `src/compat/descriptor/descriptor_engine.py`
- Existing manifest-like tooling under `tools/distribution/build_manifest.py`

## Current Dist Layout Findings

- `dist/` already ships deterministic content roots:
  - `bin/`
  - `packs/`
  - `profiles/`
  - `locks/`
  - `bundles/`
  - `registries/`
  - top-level `manifest.json`
  - top-level `lockfile.json`
- The repo `dist/` tree currently has:
  - product wrappers in `dist/bin/`
  - pack alias artifacts in `dist/packs/*/*/pack.alias.json`
  - profile bundle file `dist/profiles/bundle.mvp_default.json`
  - bundle manifest `dist/bundles/bundle.base.lab/bundle.json`
  - pack lock `dist/locks/pack_lock.mvp_default.json`

## Existing Manifest Surfaces

- `schema/install.manifest.schema` defines install identity and already carries:
  - binary hashes
  - endpoint descriptor hashes
  - build ids
- `schema/lib/artifact_manifest.schema` defines content-addressed LIB artifacts.
- `dist/manifest.json` is a legacy distribution inventory surface with:
  - file hashes
  - bundle id
  - version strings
  - canonical content hash
- `tools/distribution/build_manifest.py` is a legacy packaging-oriented manifest generator.

## Existing Build Identity Findings

- RELEASE-0 already pins deterministic build identity through:
  - `src/release/build_id_engine.py`
  - `src/compat/descriptor/descriptor_engine.py`
- Endpoint descriptors already include:
  - `extensions.official.build_id`
  - `extensions.official.semantic_contract_registry_hash`
  - deterministic platform descriptor metadata

## Existing Lock and Compat Findings

- `dist/locks/pack_lock.mvp_default.json` includes:
  - `pack_lock_hash`
  - per-pack compatibility hashes
  - profile bundle hash
- Pack alias artifacts already embed effective compatibility hashes inside `source_packs[*].compat_manifest_hash`.

## Risks Identified

- No single distribution-wide release manifest exists yet.
- `dist/manifest.json` is legacy and not the governed RELEASE-1 surface.
- Portable wrapper binaries emit live descriptors from the current source tree, so a committed release manifest would drift across later commits.
- `tools/distribution/build_manifest.py` still contains wall-clock timestamp behavior and is not acceptable as the canonical RELEASE-1 manifest engine.
- Current repo `dist/manifest.json` does not expose `semantic_contract_registry_hash`; RELEASE-1 must derive it from shipped descriptors or other shipped identity surfaces.

## Safe Insertion Points

- New governed schemas under `schema/release/` and `schemas/`
- Offline engine under `src/release/`
- CLI wrappers under `tools/release/`
- Setup verification hook in `tools/setup/setup_cli.py`
- Launcher `compat-status` augmentation in `tools/launcher/launch.py`

## Conclusion

- RELEASE-1 should add a new deterministic release manifest and verifier.
- The new manifest should be generated as a runtime distribution artifact, not committed as a locked repo artifact, because current product wrappers derive descriptor build IDs from live source revision state.
