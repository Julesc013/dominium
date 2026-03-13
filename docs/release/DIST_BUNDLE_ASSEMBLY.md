Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-2 artifact integrity verification baseline

# DIST Bundle Assembly

## Purpose

DIST-1 assembles deterministic portable distribution trees for `v0.0.0-mock`.
The assembly tool must build a canonical bundle from governed inputs without relying on the repository at runtime.

## Assembly Inputs

The bundle assembler may consume only governed inputs:

- product entry wrappers generated for:
  - `engine`
  - `game`
  - `client`
  - `server`
  - `setup`
  - `launcher`
- deterministic runtime payload needed by those products
- default store artifacts:
  - required alias-pack trees
  - default profile bundle
  - default pack lock
- default linked instance manifest
- bundled semantic contract registry surface
- generated `install.manifest.json`
- generated `manifests/release_manifest.json`
- generated `manifests/filelist.txt`
- minimal runtime docs:
  - `README`
  - `LICENSE`
  - release notes
  - compatibility instructions

## Canonical Output Root

The canonical portable output root is:

```text
dist/v0.0.0-mock/<platform_tag>/dominium/
```

All generated paths inside the bundle must be relative to that root.

## Deterministic Ordering Rules

All assembly operations must use stable ordering:

- directory creation in canonical path order
- file copy and generation sorted by normalized relative path
- runtime payload compilation sorted by normalized relative source path
- manifest entries sorted by canonical artifact key
- file list rows sorted lexicographically by normalized relative path

No output may depend on:

- wall-clock timestamps
- filesystem traversal order
- hostnames
- absolute source paths

## Runtime Payload Rules

- Python runtime code must ship as sourceless compiled modules only.
- Compiled bytecode must use deterministic invalidation data and relative `dfile` paths so host paths do not leak into artifacts.
- Runtime data files must be copied only where required by shipped products:
  - registries
  - schemas
  - MVP session template
- The bundle must not ship source `.py` files.

## Bundle Layout Rules

The assembled bundle must contain the DIST-0 portable layout:

```text
<root>/
  install.manifest.json
  semantic_contract_registry.json
  manifests/
    release_manifest.json
    filelist.txt
  bin/
  store/
    packs/
    profiles/
    locks/
  instances/
    default/
      instance.manifest.json
  saves/
  docs/
  runtime/
  LICENSE
  README
```

## Exclusion Rules

The assembly tool must exclude:

- source files
- tests
- fixtures
- `.git`
- build scripts
- temporary logs
- regression scratch files
- `__pycache__`
- `.gitkeep`

## File List Rules

`manifests/filelist.txt` must be deterministic:

- one row per shipped file except `manifests/filelist.txt` itself
- format: `<sha256>  <normalized_relative_path>`
- rows sorted lexicographically by normalized relative path

## Release Manifest Rules

The assembler must generate `manifests/release_manifest.json` from the assembled tree itself, not from repo staging inputs.
The release manifest must therefore describe the exact shipped wrapper binaries and shipped `store/*` content.

## Offline Smoke Expectations

The assembled tree must pass offline smoke checks for:

- `bin/client --descriptor`
- `bin/server --descriptor`
- `bin/setup packs verify`
- `bin/launcher instances list`
- `bin/launcher compat-status`

These smoke checks must run against the assembled bundle, not the repository.
