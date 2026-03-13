Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-2 artifact integrity verification baseline

# DIST1 Retro Audit

## Scope

DIST-1 assembles portable distribution trees for `v0.0.0-mock` without changing runtime semantics.
This audit records the current staging assumptions and the gaps between the checked-in `dist/` tree and the canonical DIST-0 bundle shape.

## Current Dist Staging Logic

- The checked-in `dist/` tree is a staging surface, not a canonical portable bundle.
- Existing `dist/bin/*` wrappers still point back into repo paths such as `tools/mvp/runtime_entry.py`, `tools/setup/setup_cli.py`, and `tools/launcher/launch.py`.
- The staged tree contains historical directories such as `cfg/`, `pkg/`, `redist/`, `registries/`, `runtime/`, `sym/`, `sys/`, and `ws/` that are not part of the DIST-0 canonical portable layout.

## Binary Output Surface

- Stable product wrapper names already exist in `dist/bin/`:
  - `engine`
  - `game`
  - `client`
  - `server`
  - `setup`
  - `launcher`
- These wrappers are not standalone today because they resolve their runtime from the repository worktree.
- `src/release/release_manifest_engine.py` currently scans `dist/bin/` for descriptor-bearing product binaries.

## Store Artifact Sources

- Required default artifacts already exist in governed repo locations:
  - `locks/pack_lock.mvp_default.json`
  - `profiles/bundles/bundle.mvp_default.json`
  - `data/session_templates/session.mvp_default.json`
- The required default pack set is represented by alias-pack trees under the current staging surface:
  - `dist/packs/base/pack.base.procedural/pack.alias.json`
  - `dist/packs/official/pack.sol.pin_minimal/pack.alias.json`
  - `dist/packs/official/pack.earth.procedural/pack.alias.json`
- These alias pack trees can be regenerated deterministically from repo packs through `tools.mvp.runtime_bundle`, so DIST-1 must not depend on the dirty staging tree.

## Install and Manifest Surfaces

- Portable install discovery currently checks adjacency at `<exe_dir>/install.manifest.json`.
- DIST-0 canonical layout places `install.manifest.json` at bundle root, not under `bin/`.
- Therefore bundle wrappers must inject `--install-root <bundle_root>` for direct launches from `bin/`.
- `tools/setup/setup_cli.py::install_manifest_payload()` can generate a valid install manifest, but its product discovery expects historical binary names such as `dominium_client` and `dominium_server`.
- DIST-1 therefore needs a custom install-manifest assembly path for the stable bundle binary names.

## Release Manifest Gap

- RELEASE-1 manifest generation currently enumerates:
  - `bin/`
  - `packs/`
  - `profiles/`
  - `locks/`
  - `bundles/`
  - `install.manifest.json`
- DIST-0 canonical layout stores shipped content under `store/packs`, `store/profiles`, and `store/locks`.
- DIST-1 therefore requires additive RELEASE-1 support for `store/*` artifact enumeration.

## Stray Dev-Only Content To Exclude

- The current staging `dist/` tree still contains dev-only or staging-only content that must not ship:
  - `__pycache__`
  - `.gitkeep`
  - staging-era helper directories not listed in DIST-0
  - repo-coupled wrappers
- The bundle assembler must generate a fresh tree instead of mutating the staging tree in place.

## DIST-1 Implications

- DIST-1 must assemble `dist/v0.0.0-mock/<platform>/dominium/` from canonical inputs, not from the checked-in staging surface.
- The assembled bundle must contain its own runtime payload and must not require the repository, Git metadata, or XStack tooling to run.
- Wrapper scripts must inject bundle-local install roots and any required offline defaults so `bin/client`, `bin/server`, `bin/setup`, and `bin/launcher` can run directly from the portable bundle.
