Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Renderer Backends

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Available
- `soft`: CPU raster + platform present. Default for auto selection.
- `null`: headless renderer with no presentation.

## Unavailable (stubbed)
- `dx9`, `dx11`, `gl2`, `vk1`, `metal`: compiled stubs are reported as
  unavailable. Explicit selection fails loudly; auto selection skips them.

## Detection
- `d_gfx_detect_backends` reports `supported` and `detail` strings.
- `d_gfx_select_backend` chooses the preferred available backend.
