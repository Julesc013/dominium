Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-1 packaged bundle baseline and DIST-2 installer constitution

# Distribution Model

## Purpose

DIST-0 freezes what a Dominium distribution means for `v0.0.0-mock`.
It defines the bundle types, required artifacts, and exclusion rules that DIST-1 packaging must satisfy.
This document does not require the current repository-backed `dist/` staging tree to already be the final shipped bundle.

## Canonical Distribution Types

### 1. Portable Full Bundle

- The user unzips the bundle and runs products directly.
- The bundle must contain:
  - `install.manifest.json`
  - `manifests/release_manifest.json`
  - `bin/`
  - `store/`
  - `instances/`
  - `saves/`
  - `docs/`
  - `LICENSE`
  - `README`

### 2. Installed Bundle

- The installed bundle has the same internal content as the portable bundle.
- An installer may register `install_id` in `install_registry.json`.
- The bundle must continue working if copied elsewhere and the registry entry disappears.

### 3. Headless Server Bundle

- Minimal runtime bundle for server operation.
- Must contain:
  - `install.manifest.json`
  - `manifests/release_manifest.json`
  - `bin/server`
  - `store/`
- It must not require rendered UI components.

### 4. Tools-Only Bundle

- Optional bundle for CLI/TUI tooling.
- Must contain:
  - `install.manifest.json`
  - `manifests/release_manifest.json`
  - governed tool binaries or wrappers under `bin/`
  - `store/`

### 5. Development Bundle

- Optional mock-only bundle for diagnostics and deeper local verification.
- `release_channel` remains `mock`.
- `stability_class` is `experimental`.
- It must still keep runtime verification offline and deterministic.

## Canonical Layout

```text
<root>/
  install.manifest.json
  manifests/
    release_manifest.json
  bin/
    engine
    game
    client
    server
    setup
    launcher
  store/
    packs/
    profiles/
    locks/
  instances/
    default/
      instance.manifest.json
  saves/
  docs/
  LICENSE
  README
```

## Required Artifact Rules

Every governed distribution must include:

- `manifests/release_manifest.json`
- `install.manifest.json`
- a pinned semantic contract registry surface
- a default linked instance
- a default `pack_lock` for the base universe

Every required artifact must be:

- content-addressed
- deterministically hashed
- verifiable offline

## Portability Rules

Portable bundles must:

- discover install root by adjacency
- use virtual paths only
- avoid mandatory environment variables
- avoid mandatory install-registry lookups
- allow direct execution from `bin/` for:
  - `engine`
  - `client`
  - `server`
  - `setup`
  - `launcher`

## Installed Mode Rules

Installed mode must:

- register `install_id` in `install_registry.json`
- keep internal paths relative or logical
- continue functioning if the install registry entry is removed and portable adjacency succeeds

## Verification Rules

Governed bundles must pass offline:

- release manifest verification
- `validate --all --profile STRICT`
- bundle verification when governed bundle artifacts are present

Verification must:

- use no network access
- detect corruption deterministically
- emit refusal codes with remediation guidance

## Exclusions

Distributions must not include:

- `.git/`
- repo-level test fixtures
- raw schema-generation tools that are not runtime-governed
- local environment files
- absolute paths in manifests
- temporary logs
- regression scratch files
- XStack tools
- debug-only flags enabled by default

## Channel and Freeze

- `release_channel = mock`
- release tag: `v0.0.0-mock`
- provisional stubs remain provisional
- experimental features are not enabled by default

## DIST-0 Scope

DIST-0 freezes the architecture and required artifact contract only.
DIST-1 is responsible for assembling a canonical bundle tree that satisfies this model exactly.
