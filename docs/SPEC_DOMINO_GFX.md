# Renderer API (dgfx)

Public header: `include/domino/gfx.h`  
Null backend: `source/domino/render/gfx.c`

## dgfx IR snapshot
- Opaque `dgfx_context` created via `dgfx_init(const dgfx_desc*)`; desc selects backend (`NULL/SOFT8/GL2/DX9/VK1`), optional `dsys_window*`, width/height, and vsync flag.
- `dgfx_caps` reports a backend name plus feature bits; the NULL backend reports all capabilities as false and `max_texture_size = 0`.
- Frame flow is a no-op stub: `dgfx_begin_frame`/`dgfx_execute`/`dgfx_end_frame` exist for future backends and simply return.
- `dgfx_resize` only updates stored dimensions inside the context; no swapchain work is performed.

## Command buffer
- Caller owns a linear buffer: `dgfx_cmd_buffer { data, size, capacity }`.
- `dgfx_cmd_emit` appends `{dgfx_cmd header + payload bytes}` when space permits; returns `false` if capacity would be exceeded.
- `dgfx_cmd_buffer_reset` rewinds `size` to zero without touching the underlying storage.

### Command header
- `dgfx_cmd { dgfx_opcode op; uint16_t payload_size; }` is written verbatim (little-endian). The struct may be padded by the compiler, but payload starts immediately after `sizeof(dgfx_cmd)` as emitted by the producer.
- `payload_size` describes **only** the payload bytes following the header.

### Payload layouts (current set)
- `DGFX_CMD_CLEAR` payload: `{uint8_t r, g, b, a}` for a flat clear colour.
- `DGFX_CMD_DRAW_LINES` payload:  
  - `dom_gfx_lines_header { uint16_t vertex_count; uint16_t reserved; }`  
  - followed by `vertex_count` packed vertices: `dom_gfx_line_vertex { float x; float y; float z; uint32_t color; }` (stride 16 bytes). Colours are opaque ARGB/Little-endian integers; z is currently unused but reserved for isometric elevation.

## Legacy compatibility
- The legacy `domino_gfx_*` surface API remains declared for the existing software renderer and tests; it is unchanged but considered legacy alongside the new dgfx IR.

## Minimal stub usage
```c
uint8_t scratch[256];
dgfx_desc desc = { DGFX_BACKEND_NULL, NULL, 800, 600, 1 };
dgfx_context* ctx = dgfx_init(&desc);

dgfx_cmd_buffer buf;
buf.data = scratch;
buf.size = 0;
buf.capacity = sizeof(scratch);
dgfx_cmd_emit(&buf, DGFX_CMD_CLEAR, NULL, 0);

dgfx_begin_frame(ctx);
dgfx_execute(ctx, &buf);
dgfx_end_frame(ctx);
dgfx_shutdown(ctx);
```

No pixels are produced yet; this stub only wires the ABI so future backends can drop in.

## DX9 Renderer Backend (Direct3D 9)
- Backend: `DGFX_BACKEND_DX9`, HAL Direct3D 9 device with windowed swap chain.
- Targets: Windows XP through Windows 10+ (32-bit process).
- Features: 2D via TL quads and line lists; 3D triangle lists stubbed for future DrawIndexedPrimitiveUP usage; vector overlays via lines; text is currently a no-op.
- Integration: requires the Win32 dsys backend; pass the Win32 `HWND` exposed by `dsys_window_get_native_handle` inside `dgfx_desc.window`; `dgfx_desc.vsync` toggles Present interval.
- Limitations: fixed-function style states only (no shaders yet); minimal device-loss handling (Reset on resize only); text rendering is not implemented in v1.

## Canvas builders (Dominium)
`dom_canvas_build(core, inst, canvas_id, dom_gfx_buffer*)` dispatches to Dominium helpers to populate dgfx commands:
- `world_surface` — clears then draws a 10x10 top-down grid (chunk preview).
- `world_orbit` — clears then draws concentric orbit rings and a player marker.
- `construction_exterior` — clears then draws a bounding box outline for a construction.
- `construction_interior` — clears then draws a simple multi-room floor grid.

Unknown `canvas_id` values currently yield an empty buffer and succeed.
