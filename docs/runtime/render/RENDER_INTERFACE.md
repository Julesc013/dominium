Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Renderer Interface (DGFX)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/archive/audit/CANON_MAP.md` and `docs/archive/audit/DOC_DRIFT_MATRIX.md`.


This document describes the renderer interface exposed by `dgfx_*`/`d_gfx_*`.
Render backends are logical plugins selected at runtime; no renderer-specific
logic lives in engine/game subsystems.

## Versioning
- Protocol: `DGFX_PROTOCOL_VERSION`
- ABI vtables: `dgfx_ir_api_v1`, `dgfx_native_api_v1`
- Interface IDs: `DGFX_IID_IR_API_V1`, `DGFX_IID_NATIVE_API_V1`
- Entry: `dgfx_get_ir_api(1, &api)` returns the vtable

## Backend registry and detection
- `dom_dgfx_register_caps_backends` registers compiled backends in `dom_caps`
- `d_gfx_detect_backends` enumerates availability; `detail` is the reason string
- `d_gfx_select_backend` chooses the preferred available backend

## Selection policy
- Explicit selection: `d_gfx_init("name")` or `dgfx_desc.backend` must fail
  loudly when unavailable (no silent fallback)
- Auto selection: pass NULL/"auto"/"default" and the best backend is chosen;
  selection is logged to stderr with the reason string

## Renderer lifecycle
- Init/shutdown: `d_gfx_init`, `d_gfx_shutdown`
- Frame: `d_gfx_cmd_buffer_begin`, `d_gfx_submit`, `d_gfx_present`
- Surface binding: `d_gfx_bind_surface`, `d_gfx_resize`, `d_gfx_get_native_window`

## Built-in backends
- `null`: headless renderer, no presentation (use for tests/servers)
- `software`: CPU buffer + platform present (`d_system_present_framebuffer` with native window); current runtime alias is `soft`
- `opengl`: planned first hardware family, target OpenGL 3.3 core-style shader pipeline; current transitional alias is `gl4`
- `direct3d`: planned Windows hardware family, primary version Direct3D 11; current transitional alias is `dx11`
- `metal` and `vulkan`: later advanced families; current Vulkan transitional alias is `vk1`
- `opengl_2_1`, `opengl_1_1`, and `direct3d_9`: back-port/research lanes; current transitional aliases include `gl2`, `gl1`, and `dx9`
- explicit selection of unavailable compiled stubs fails loudly until real backends land

## Capabilities
- Opcode mask: `d_gfx_get_opcode_mask` and `d_gfx_get_opcode_mask_for_backend`
- Unsupported opcodes are filtered per backend (no silent backend swap)

## Shader cache policy
- Shader caches are disposable and never required for boot
