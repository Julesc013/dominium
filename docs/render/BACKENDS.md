Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Renderer Backends

## Available
- `soft`: CPU raster + platform present. Default for auto selection.
- `null`: headless renderer with no presentation.

## Unavailable (stubbed)
- `dx9`, `dx11`, `gl2`, `vk1`, `metal`: compiled stubs are reported as
  unavailable. Explicit selection fails loudly; auto selection skips them.

## Detection
- `d_gfx_detect_backends` reports `supported` and `detail` strings.
- `d_gfx_select_backend` chooses the preferred available backend.