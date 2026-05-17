# MOVE-FAMILY-00-REFINE IDE Manifest Boundaries

Status: DERIVED
Last Reviewed: 2026-05-17

## Summary

`ide/README.md` has already moved to `docs/architecture/IDE_PROJECTIONS.md`. The remaining tracked `ide/` files are machine-readable projection metadata:

- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

## Ownership Decision

Preferred owner: `contracts/projections`.

Proposed future paths:

- `contracts/projections/ide/projection_manifest.schema.json`
- `contracts/projections/ide/examples/example_linux_clang_modern_client_gui.projection.json`
- `contracts/projections/ide/examples/example_win_vc6_win9x_client_gui.projection.json`

## Why Not Other Owners

- `docs/architecture`: already owns human explanation, not machine-readable schema/example authority.
- `archive/generated`: these files are tracked source metadata, not generated output evidence.
- `tools/ide`: tools consume the manifests, but the manifests define contract shape rather than tool implementation.
- `runtime/ide`: no runtime IDE implementation owner is established.
- `contracts/ide`: acceptable only as a sub-namespace, but `contracts/projections` is the stronger owner because projection identity is the core contract.

## Consumer Evidence

- `scripts/verify_docs_sanity.py` checks `ide/manifests/projection_manifest.schema.json`.
- `scripts/ide_gen.sh` writes generated projection manifests under `ide/manifests/`.
- `cmake/ide/IdeProjectionManifest.cmake` writes generated projection manifests under `ide/manifests/`.
- Architecture docs and audit evidence reference `ide/manifests/**`.

## Required Before Move

- Add an explicit projection manifest contract location.
- Add or identify a schema/manifest validator.
- Produce a reference rewrite plan for CMake, scripts, docs, and generated evidence posture.
- Keep apply disabled until a later gate approves exact paths.
