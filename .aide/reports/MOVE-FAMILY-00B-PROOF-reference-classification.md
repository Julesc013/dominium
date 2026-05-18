Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00B-PROOF Reference Classification

## Status

Result: PASS_WITH_WARNINGS.

## Blocking Scan

The targeted blocker scan found zero active references to the retired tracked source schema/example paths in active script, tool, CMake, test, `.gitignore`, or current architecture surfaces.

Retired source paths checked:

- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

## Remaining Old-Path Reference Classes

| Class | Status | Notes |
| --- | --- | --- |
| Generated-output producer references | warning-only | `scripts/ide_gen.sh`, `scripts/ide_gen.bat`, `cmake/ide/IdeProjectionManifest.cmake`, and `data/release/preset_and_toolchain_registry.json` still refer to generated `ide/manifests/*.projection.json` output. |
| Current architecture generated-output docs | warning-only | `docs/architecture/IDE_PROJECTIONS.md` and `docs/architecture/PROJECTION_LIFECYCLE.md` intentionally preserve the generated output path while pointing schema authority at `contracts/projection/ide`. |
| Root-recycling history | warning-only | MOVE-FAMILY plan/gate/apply docs preserve the old paths as move history. |
| AIDE context/evidence | warning-only | `.aide/refactors/**`, `.aide/reports/**`, `.aide/roots/**`, `.aide/repo/**`, and related AIDE evidence preserve historical inventory and plan paths. |
| Planning/audit evidence | warning-only | `docs/audit/**`, `docs/planning/**`, and `data/planning/**` preserve older scan and planning records. |

## New Path References

Current active references now point at:

- `contracts/projection/ide/projection_manifest.schema.json`
- `contracts/projection/ide/examples/example_linux_clang_modern_client_gui.projection.json`
- `contracts/projection/ide/examples/example_win_vc6_win9x_client_gui.projection.json`

## Decision

No stale active source/tool/validator/current-doc blocker remains. The remaining old-path references are accepted as historical, planning, audit, AIDE evidence, root-recycling history, or generated-output policy references.
