Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Renderer Backends

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/archive/audit/CANON_MAP.md` and `docs/archive/audit/DOC_DRIFT_MATRIX.md`.


## Available
- `null`: headless renderer with no presentation.
- `software`: CPU raster + platform present. Current runtime alias: `soft`.

## Primary Planned Hardware Families

- `opengl`: first hardware renderer family, targeting an OpenGL 3.3 core-style shader pipeline. Current transitional alias: `gl4`.
- `direct3d`: Windows hardware renderer family, primary version Direct3D 11. Current transitional alias: `dx11`.

## Later Advanced Families

- `metal`: later Apple-native renderer, not required for the Mac OS X 10.9.5 baseline.
- `vulkan`: later explicit-GPU renderer. Current transitional alias: `vk1`.
- `direct3d_12`: advanced Windows lane. Current transitional alias: `dx12`.

## Back-Port / Research Lanes

- `opengl_2_1`, `opengl_1_1`, and `direct3d_9` remain research/back-port lanes. Current transitional aliases include `gl2`, `gl1`, and `dx9`.
- Explicit selection of unavailable compiled stubs fails loudly; auto selection skips them.

## Drawing

- `canvas`: renderer-independent drawing feature layer. `vector2d` is a transitional feature alias, not a renderer backend identity.

## Detection
- `d_gfx_detect_backends` reports `supported` and `detail` strings.
- `d_gfx_select_backend` chooses the preferred available backend.
