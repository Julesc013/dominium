Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Platform ID Canon

## Scope

This document defines canonical platform identity tokens used by distribution,
packaging manifests, setup/launcher resolution, RepoX, and TestX.

## Canonical Platform IDs

The only valid platform IDs are:

- `winnt`
- `win9x`
- `win16`
- `dos`
- `macosx`
- `macclassic`
- `linux`
- `android`
- `ios`
- `web`

## Forbidden Aliases

The following aliases are forbidden in runtime code, manifests, registries, and
distribution paths:

- `win`
- `windows`
- `mac`
- `osx`

Docs may mention aliases only for migration or operator guidance.

## Arch And ABI

- `arch` values are explicit data tokens (for example `x86_64`, `x86_32`,
  `arm64`, `wasm32`).
- `abi` values are namespaced (`abi:<platform>:<toolchain>`).
- Package manifests MUST use tuples declared in
  `data/registries/platform_registry.json`.

## Compression Policy Metadata

Platform registry entries carry compression compatibility metadata in
`extensions.compression_support`:

- `deflate` is required.
- optional algorithms (for example `zstd`) are declared but not required.

## Additions

To add a platform:

1. Add tuple(s) to `data/registries/platform_registry.json`.
2. Keep IDs canonical and lower-case.
3. Add any new ABI IDs explicitly.
4. Update RepoX/TestX enforcement and docs in the same change.
