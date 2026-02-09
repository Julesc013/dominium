Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Dist PKG Pipeline

## Scope

This document defines deterministic packaging automation targets and their CI
contract.

## Canonical Targets

- `pkg_pack_all`
- `pkg_verify_all`
- `pkg_index_all`
- `dist_build_manifest`
- `install_from_pkg_cache`
- `setup_install_smoke`
- `launcher_run_smoke`

## CI Execution Order

1. Build strict binaries.
2. Regenerate derived UI binding artifacts (`ui_bind_phase`).
3. `pkg_pack_all`
4. `pkg_verify_all`
5. `pkg_index_all`
6. `dist_build_manifest`
7. `install_from_pkg_cache`
8. Smoke checks (`setup_install_smoke`, `launcher_run_smoke`)

## Required Outputs

- Package artifacts under `dist/pkg/<platform>/<arch>/`.
- Package index artifact under `dist/meta/<platform>/<arch>/`.
- Build manifest under `dist/meta/build_manifest.json`.

## Failure Policy

- Any package verification failure is blocking.
- Any install projection digest mismatch is blocking.
- Any smoke run nondeterminism is blocking.
