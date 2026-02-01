Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Renderer Interface (DGFX)

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
- `soft`: CPU buffer + platform present (`d_system_present_framebuffer` with native window)
- `null`: headless renderer, no presentation (use for tests/servers)
- `dx9`/`dx11`/`gl2`/`vk1`/`metal`: compiled stubs are reported as unavailable;
  explicit selection fails loudly until real backends land

## Capabilities
- Opcode mask: `d_gfx_get_opcode_mask` and `d_gfx_get_opcode_mask_for_backend`
- Unsupported opcodes are filtered per backend (no silent backend swap)

## Shader cache policy
- Shader caches are disposable and never required for boot