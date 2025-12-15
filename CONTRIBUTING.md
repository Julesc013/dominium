# Dominium — Contributing (Authoritative)

This repository is specification-driven: behavioral and format changes must be
reflected in the spec set under `docs/` and must preserve determinism and hard
layering.

## Repository structure
`docs/DIRECTORY_CONTEXT.md` is the authoritative directory/layout contract.

## Mandatory constraints
- Determinism: `docs/SPEC_DETERMINISM.md` and `docs/DETERMINISM_REGRESSION_RULES.md`
- Placement: anchors + quantized poses (`docs/SPEC_POSE_AND_ANCHORS.md`)
- Authoring vs compiled: compiled artifacts are derived caches
  (`docs/SPEC_TRANS_STRUCT_DECOR.md`)
- Language/toolchain: `docs/LANGUAGE_POLICY.md`
- Style/naming: `docs/STYLE.md`

## Contribution workflow
1. Identify the relevant spec(s) under `docs/` for the area you are changing.
2. If behavior/format changes, update the spec(s) first (or in the same PR).
3. Keep changes within module boundaries (no private header peeking across
   subsystems).
4. Run tests and determinism checks:
   - Build: see `docs/BUILDING.md`
   - Run: `ctest --test-dir build`
   - Determinism scan: `ctest -R domino_det_regression_scan_test`

## What will be rejected
- Introducing non-determinism in deterministic core paths (unordered iteration,
  wall-clock, platform APIs, float/double math).
- Treating derived caches (compiled artifacts, render geometry, UI state) as
  authoritative state.
- Cross-layer mutation or shortcut access that violates the subsystem boundaries
  documented in the spec set.
