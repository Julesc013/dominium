# Renderer API (dgfx)

Public header: `include/domino/gfx.h`  
Null backend: `source/domino/render/gfx.c`

## dgfx IR snapshot
- Opaque `dgfx_context` created via `dgfx_init(const dgfx_desc*)`; desc selects backend (`NULL/SOFT8/GL2/DX9/VK1/DX7/DX11/METAL/QUARTZ/QUICKDRAW/GDI`), optional `dsys_window*`, width/height, and vsync flag.
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

## DX11 Renderer Backend (Direct3D 11)
- Backend: `DGFX_BACKEND_DX11`, Direct3D 11 device, immediate context, and DXGI swap chain.
- Targets: Windows 7 and later (32-bit or 64-bit process).
- Features: hardware-accelerated 2D/3D paths; sprites/meshes/lines routed through simple D3D11 pipelines; text is stubbed for now; alpha blending and depth states are created.
- Integration: requires the Win32 dsys backend; pass the Win32 `HWND` from `dsys_window_get_native_handle` via `dgfx_desc.window`; swap chain sizes derive from `dgfx_desc.width/height`; `dgfx_desc.vsync` feeds the Present sync interval.
- Limitations: shaders/input layouts are placeholder; text rendering unimplemented; MSAA/fullscreen toggles are not exposed yet.

## GL2 Renderer Backend (OpenGL 2.x) — gl2
- Backend: `DGFX_BACKEND_GL2`, OpenGL 2.0–2.1 programmable pipeline with GLSL shaders.
- Targets: Win32 (wgl), Linux/X11 (glX), macOS (NSOpenGL/CGL) where GL2 contexts are available.
- Features: 2D sprites, 3D meshes, and vector lines using simple shader programs; alpha blending and depth testing are enabled by default.
- Integration: use the dsys window backend and pass the native handle via `dgfx_desc.window` (e.g., Win32 `HWND`); viewport size comes from `dgfx_desc.width/height`.
- Limitations: text rendering is stubbed; GLX/Cocoa context creation is placeholder; no MSAA/sRGB configuration in this revision.

## Metal Renderer Backend (Metal)
- Backend: `DGFX_BACKEND_METAL`, Metal device/command queue rendering into a `CAMetalLayer` swapchain.
- Targets: macOS 10.11+ on Intel or Apple Silicon.
- Features: hardware-accelerated 2D/3D and line rendering with alpha blend and depth-state defaults; text is stubbed for now.
- Integration: requires the Cocoa dsys backend; pass the `NSWindow*` from `dsys_window_get_native_handle` via `dgfx_desc.window`; the backend creates/configures a `CAMetalLayer` on the window’s content view and sizes it from `dgfx_desc.width/height`; `dgfx_desc.vsync` is honored at present time.
- Limitations: texture binding and text are placeholders; pipelines are minimal and MSAA/advanced features are not exposed yet.

## GDI Renderer Backend (gdi) — Windows 3.x → 11
- Backend: `DGFX_BACKEND_GDI`, Win16/Win32 GDI API (HDC, HBITMAP, BitBlt/StretchBlt, MoveToEx/LineTo/Rectangle).
- Targets: Windows 3.x, Windows 95/98/ME, Windows NT/2000/XP, Windows 7–11 (32/64-bit process).
- Features: 2D via a 32-bit ARGB DIB section as an offscreen framebuffer, BitBlt to the window DC; vector primitives via GDI pens/lines; basic filled-rect sprites via solid brushes.
- Integration: requires the Win32/Win16 dsys backend; pass the `HWND` returned by `dsys_window_get_native_handle` through `dgfx_desc.window`; framebuffer dimensions come from `dgfx_desc.width/height`; vsync is OS-managed.
- Limitations: `supports_3d` = false, mesh/text/texture commands are no-ops in v1; alpha/blending beyond what BitBlt offers is not implemented; performance is bounded by GDI BitBlt throughput and OS compositor.

## QuickDraw Renderer Backend (quickdraw) — Mac OS 7/8/9
- Backend: `DGFX_BACKEND_QUICKDRAW`, Classic Mac OS QuickDraw API using a window port plus an offscreen GWorld for double buffering.
- Targets: Mac OS 7, 8, 9; early Carbon/Classic environments where QuickDraw is present.
- Features: 2D and vector primitives via MoveTo/LineTo and PaintRect; raster blits via CopyBits from the offscreen GWorld; meshes and text are stubbed; alpha support follows QuickDraw capabilities.
- Integration: requires the Classic/Carbon dsys backend; pass the native Mac window handle returned by `dsys_window_get_native_handle` through `dgfx_desc.window`; the backend allocates an offscreen GWorld sized to `dgfx_desc.width/height` and blits to the window each frame.
- Limitations: no hardware 3D pipeline; textures and text are not implemented in v1; resizing recreates the offscreen buffer; blending is limited to what QuickDraw offers.

## Quartz 2D Renderer Backend (quartz) — macOS 10.4+
- Backend: `DGFX_BACKEND_QUARTZ`, Quartz/CoreGraphics 2D backend that renders into an RGBA CGBitmapContext and blits to the window’s CGContext each frame.
- Targets: macOS 10.4+ (Intel/ARM) with the Cocoa dsys backend supplying an NSWindow/NSView native handle.
- Features: supports_2d=true, supports_3d=false, supports_alpha=true; lines and filled sprites mapped to CGContext drawing with simple camera offsets; text and textures are stubbed in v1.
- Integration: pass the Cocoa `dsys_window*` in `dgfx_desc.window`; the native handle is used to fetch a `CGContextRef` for presentation while the backend renders into a premultiplied 8:8:8:8 bitmap sized to `dgfx_desc.width/height`.
- Limitations: no native 3D path; viewport/pipeline handling is minimal; presentation depends on a Cocoa helper returning a valid window context; text/texture drawing is not implemented yet.

## Vulkan 1.0 Renderer Backend (vk1)
- Backend: `DGFX_BACKEND_VK1`, Vulkan 1.0 device with a single graphics/present queue.
- Targets: Windows, Linux, macOS (via MoltenVK) where Vulkan 1.0 and a compatible surface extension are available.
- Features: 2D sprites/quads, 3D mesh path, and vector/line primitives routed through dedicated pipelines; text is currently a no-op; alpha/raster fully supported once pipelines are provided.
- Integration: requires a valid `dsys_window*`; the backend maps `dsys_window_get_native_handle` to a `VkSurfaceKHR` using platform-specific creation (Win32/X11/Metal hooks to be wired). Set `dgfx_desc.backend = DGFX_BACKEND_VK1`, width/height from the descriptor, and vsync mapped to present mode.
- Limitations: platform surface creation is stubbed in the initial drop; descriptor management, streaming buffers, and text are deferred; swapchain recreation on resize is basic.

## Canvas builders (Dominium)
`dom_canvas_build(core, inst, canvas_id, dom_gfx_buffer*)` dispatches to Dominium helpers to populate dgfx commands:
- `world_surface` — clears then draws a 10x10 top-down grid (chunk preview).
- `world_orbit` — clears then draws concentric orbit rings and a player marker.
- `construction_exterior` — clears then draws a bounding box outline for a construction.
- `construction_interior` — clears then draws a simple multi-room floor grid.

Unknown `canvas_id` values currently yield an empty buffer and succeed.
