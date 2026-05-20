# PORTABILITY-MATRIX-01 Initial Portability Inventory

Status: PASS_WITH_WARNINGS
Task: PORTABILITY-MATRIX-01
Starting HEAD: `2a9c1dc11cf139b82343a08a78297ea3fe1333a0`

## Summary

The repository already has release-era planning and proof artifacts for build, target, component, product boot, packaging, and platform matrices. This task does not retrofit them into support claims. It classifies them as evidence sources or future migration inputs for `contracts/platform/**`.

## Inventory Counts

- Build-proven target evidence candidates: 18.
- Smoke-proven target evidence candidates: 100.
- Product-proven target evidence candidates: 14.
- Release-proven target evidence candidates: 171.
- Planned target candidates: 18.
- Research target candidates: 2069.
- Historical candidates: 338.
- Unknown/deferred portability candidates: 246.

## Current Evidence Sources

- Build and toolchain contracts: `contracts/build/**`.
- Release component matrix: `contracts/release/component_matrix.contract.toml`.
- Release platform/toolchain/product/package docs: `docs/release/PLATFORM_MATRIX.md`, `docs/release/TOOLCHAIN_MATRIX.md`, `docs/release/PRODUCT_MODE_MATRIX.md`, `docs/release/PACKAGING_MATRIX.md`, `docs/release/PRODUCT_BOOT_PROOF.md`, `docs/release/PORTABLE_PROJECTION_PROOF.md`.
- Product boot and distribution audit artifacts: `contracts/audit/product_boot_matrix.json`, `contracts/audit/dist_platform_matrix.json`, `docs/archive/audit/convergence_steps/product_boot_matrix.md`.
- Current fast strict proof: `.aide/reports/PORTABILITY-MATRIX-01-fast-strict.md`.

## Classification Notes

- Current host/headless and MSVC v143 lanes are treated as build/smoke proof lanes only.
- Linux, macOS, legacy Windows, old MSVC, VC6, CodeWarrior, WASM, OpenGL, Direct3D, Metal, Vulkan, installer, and signed release lanes remain planned or research unless later proof exists.
- Existing release docs are valuable evidence references, but older planning status terms do not become `supported` without the new matrix proof requirements.
- No new build target, CMake preset, CI job, provider, renderer, package runtime, or release artifact was created.
