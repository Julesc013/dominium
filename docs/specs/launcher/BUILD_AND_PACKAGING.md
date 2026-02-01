Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Build and Packaging

Doc Version: 1

This document describes how to build the launcher reproducibly and how to produce deterministic distribution artifacts for Tier-1 platforms.

## Building

- CMake-based build (C++98).
- Prefer Ninja generators for CI and local determinism.
- Networking can be disabled for offline-capable builds.

See `docs/guides/BUILDING.md` and `docs/ci/BUILD_MATRIX.md` for full matrices.

## Build Metadata

Binaries embed:
- build id
- git commit hash
- toolchain id

These values are surfaced via the launcher’s profiling/audit output.

## Reproducible Builds

Supported toolchains enable deterministic build flags where available. A verification script builds twice and compares binary hashes.

- Verification script: `scripts/repro/verify_reproducible_builds.py`
- Deterministic timestamps: `SOURCE_DATE_EPOCH` may be used by packaging and archive steps.

## Deterministic Archives

Portable packages and diagnostic bundles use deterministic archive creation to ensure stable ordering and timestamps.

- Archive helper: `scripts/packaging/make_deterministic_archive.py`
- Crash/support bundles: `scripts/diagnostics/make_support_bundle.py`

## Packaging Outputs

Packaging is performed by staging a distribution root and then producing deterministic archives/installers:

- Windows:
  - Portable ZIP
  - Installer (MSI or bundled installer wrapper)
- macOS:
  - `.app` bundle
  - Optional codesign hooks (may be stubbed)
- Linux:
  - Portable tarball
  - Optional AppDir-like layout

Packaging must not introduce hard-coded paths in launcher core; distribution wrappers set an explicit home/root for execution.

See `docs/specs/launcher/ARCHITECTURE.md` and `docs/specs/CONTRACTS.md`.