# Renderer API (dgfx)

Public header: `include/domino/gfx.h`  
Null backend: `source/domino/render/gfx.c`

## dgfx IR snapshot
 - Opaque `dgfx_context` created via `dgfx_init(const dgfx_desc*)`; desc selects backend (`NULL/SOFT/SOFT8/GL2/DX9/VK1/DX7/DX11/METAL/QUARTZ/QUICKDRAW/CGA/MDA/EGA/VGA/XGA/GDI/VESA/HERC`), optional `dsys_window*`, width/height, and vsync flag.
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

## Unified Software Renderer Backend (soft) — All Platforms
- Backend: `DGFX_BACKEND_SOFT` (also selected by `DGFX_BACKEND_SOFT8`); single CPU rasterizer replacing prior soft8/soft16/soft32/softref/fallback/null concepts through profiles.
- Profiles: `NULL` (ignore IR, no framebuffer), `FAST` (speed-first, 16bpp RGB565, depth16, no stencil/subpixel/MSAA), `BALANCED` (default; 32bpp ARGB, depth24, stencil8), `REFERENCE` (32bpp ARGB, depth32, stencil8, high-precision/subpixel paths enabled).
- Pixel formats: 8bpp indexed, 16bpp RGB565, 32bpp ARGB; optional depth (16/24/32) and stencil (8). All primitives render into one contiguous software framebuffer.
- Mixed 2D/3D: sprites/rects, vector lines, and 3D triangles share the same surface; IR order controls stacking (world then HUD). Depth writes/reads obey the profile; text/texture sampling are stubbed initially.
- Presentation: platform-agnostic blit hook (`soft_present_fn`) copies the framebuffer to the OS surface (DOS blitter, GDI BitBlt, X11 PutImage, Quartz/CoreGraphics, SDL texture, etc.). If unset, rendering stays offscreen without failing.
- Deterministic: single-threaded CPU math only; no GPU/OS headers in the core raster; consistent results across targets given identical IR and configuration.

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

## VGA Renderer Backend (vga) — DOS16/DOS32
- Backend: `DGFX_BACKEND_VGA`, classic VGA mode 13h (320×200×8 indexed) rendered via the software rasterizer into system RAM and blitted to 0xA0000 VRAM (`source/domino/render/vga/vga_gfx.c`, `vga_hw.c`).
- Targets: DOS 3.x–6.x, DOS extenders/DOS32, and VGA-compatible DOS boxes/emulators.
- Features: 2D/3D/vector command paths reuse `soft_raster` routines; optional depth/stencil live in system RAM; palette is the default VGA DAC with simple RGBA→index quantization; alpha not supported.
- Integration: full-screen only, ignores `dgfx_desc.window`; resolution fixed to 320×200; `dgfx_desc.width/height` act as hints; vsync is not modeled.
- Limitations: fixed palette/resolution, no runtime resize; textures/meshes/text are stubs in v1; palette management beyond defaults is future work.

## Hercules Renderer Backend (herc) — Monochrome DOS
- Backend: `DGFX_BACKEND_HERC`, Hercules Graphics Card class 720×348 1bpp graphics driven by the shared software rasterizer and packed into the Hercules interlaced VRAM layout.
- Targets: DOS16 PCs with Hercules or Hercules-compatible adapters (or emulators such as DOSBox/PCem/86Box); fullscreen only and ignores `dgfx_desc.window`.
- Features: CPU software pipeline for 2D/3D/vector commands into an 8bpp RAM framebuffer with optional depth/stencil; `herc_hw_blit_720x348` thresholds brightness to on/off bits and stores bytes to segment 0xB000 using the 4-bank scanline layout.
- Integration: fixed 720×348 resolution; begin/end frame clear and blit the RAM buffer; `herc_hw_set_mode_720x348`/`herc_hw_restore_text_mode` wrap BIOS/port I/O for real DOS targets (stubbed in hosted builds).
- Limitations: monochrome output (no alpha/colour), no runtime resize, text/texture/mesh paths are stubbed in v1; real hardware blits require platform-specific `herc_hw` implementations.

## QuickDraw Renderer Backend (quickdraw) — Mac OS 7/8/9
- Backend: `DGFX_BACKEND_QUICKDRAW`, Classic Mac OS QuickDraw API using a window port plus an offscreen GWorld for double buffering.
- Targets: Mac OS 7, 8, 9; early Carbon/Classic environments where QuickDraw is present.
- Features: 2D and vector primitives via MoveTo/LineTo and PaintRect; raster blits via CopyBits from the offscreen GWorld; meshes and text are stubbed; alpha support follows QuickDraw capabilities.
- Integration: requires the Classic/Carbon dsys backend; pass the native Mac window handle returned by `dsys_window_get_native_handle` through `dgfx_desc.window`; the backend allocates an offscreen GWorld sized to `dgfx_desc.width/height` and blits to the window each frame.
- Limitations: no hardware 3D pipeline; textures and text are not implemented in v1; resizing recreates the offscreen buffer; blending is limited to what QuickDraw offers.

## CGA Renderer Backend (cga) — DOS16 / Emulated CGA
- Backend: `DGFX_BACKEND_CGA`, IBM CGA graphics mode 4/5 targeting 320x200 with four colours (2 bpp packed).
- Targets: DOS16 PCs (PC/XT/AT) or CGA-compatible emulators (DOSBox/PCem/86Box). Runs fullscreen; ignores `dgfx_desc.window`.
- Features: CPU software drawing into an 8bpp system-RAM buffer with simple line/sprite primitives; each frame quantizes to 2-bit colour codes and packs 4 pixels per byte before writing to CGA VRAM (0xB800 segment) via `cga_hw_blit_320x200_4col`.
- Integration: fixed resolution; palette 0 selected in `cga_hw_set_mode_320x200_4col`; begin/end frame drive the blit; caps report 2D only, meshes/text/texture paths stubbed.
- Limitations: no resize, no alpha or texture support, only four hardware colours; hardware mode set/VRAM writes require a DOS-specific `cga_hw` implementation (stubbed on non-DOS builds).

## MDA Renderer Backend (mda) — 720×350 Monochrome
- Backend: `DGFX_BACKEND_MDA`, IBM Monochrome Display Adapter graphics treated as a 720x350 1bpp framebuffer at segment 0xB000.
- Targets: DOS16 PCs or MDA-compatible emulators; fullscreen only and ignores `dgfx_desc.window`.
- Features: CPU software rasterizer renders into an 8bpp grayscale RAM framebuffer, then `mda_hw_blit_720x350` thresholds (>=128) to 1-bit, packs 8 pixels per byte, and writes using the interlaced MDA scanline layout; supports line and filled-rect IR paths plus future CPU triangles; text/texture commands are stubbed.
- Integration: `mda_hw_set_mode_720x350` programs the mode; begin/end frame clear system RAM buffers and flush to VRAM each frame; optional depth/stencil live in RAM alongside the color buffer.
- Limitations: single-bit output (no grayscale on the display), fixed 720x350 resolution with no runtime resize, and bandwidth is limited by CPU bit-pack/blit cost and legacy VRAM timing.

## EGA Renderer Backend (ega) — DOS16/DOS32
- Backend: `DGFX_BACKEND_EGA`, IBM EGA planar 16-colour graphics targeting 640x350 mode 10h-style output.
- Targets: DOS16/DOS32 PCs or EGA-compatible emulators; fullscreen only, ignores `dgfx_desc.window`.
- Features: CPU software rasterizer renders into an 8bpp indexed `soft_framebuffer` with optional depth/stencil; `ega_hw_blit_640x350_16` clamps to 16 palette indices and packs four bitplanes per scanline; 2D/3D/vector paths reuse the shared software rasterizer; text/texture/mesh commands are stubbed in v1.
- Integration: `ega_hw_set_mode_640x350_16` switches the display; begin/end frame clear the RAM buffer and flush to planar VRAM each frame; palette programming is left to BIOS defaults in this revision.
- Limitations: fixed 640x350 resolution for v1, no dynamic resize, palette control is stubbed, and DOS-specific `ega_hw` implementations are required for real hardware VRAM writes.

## XGA Renderer Backend (xga) — Early PC Framebuffer
- Backend: `DGFX_BACKEND_XGA`, IBM XGA/XGA-2 class framebuffer treated as an 8bpp indexed linear (or banked) surface.
- Targets: DOS16/DOS32, OS/2, early Windows, or emulators exposing XGA-like VRAM; fullscreen/framebuffer only, ignores `dgfx_desc.window`.
- Features: CPU software rasterizer renders into an 8bpp `soft_framebuffer` with optional depth/stencil; `xga_hw_blit` copies the RAM buffer to XGA VRAM each `end_frame`; supports mixed 2D/3D/vector IR via the shared software pipeline; palette handling relies on the default XGA palette in v1.
- Integration: chooses the closest supported mode to the requested size (defaults 640x480x8, opts into 800x600x8 when hinted); `xga_hw_set_mode`/`xga_hw_restore_mode` wrap platform BIOS/driver calls; presentation uses a full-frame blit.
- Limitations: discrete resolutions only (no runtime resize), palette programming is stubbed, mesh/text/texture commands are placeholders; real hardware support depends on replacing the `xga_hw` stubs with banking/linear VRAM writes.

## VESA BIOS Renderer Backend (vesa) — DOS/Win16/Win32 DOS boxes
- Backend: `DGFX_BACKEND_VESA`, VBE 2.0+ BIOS path that programs a fullscreen VESA graphics mode and treats the linear framebuffer as the software renderer’s color buffer.
- Targets: DOS16/32, Win3.x DOS sessions, Win9x/NT DOS boxes, or any emulator exposing a VESA LFB.
- Features: CPU software pipeline for 2D/3D/vector; depth/stencil live in system RAM; supports 8/16/32 bpp depending on the selected mode; text/textures/mesh decoding are stubbed in v1.
- Integration: `dgfx_desc.window` is ignored; pass desired width/height (defaults 640x480) and the backend tries 32bpp then 16bpp modes before giving up; draws directly into VRAM via `soft_raster_*` and clears/presents in place.
- Limitations: requires VBE LFB support; banked/framebuffer blits and runtime resize are not implemented yet; present is implicit because VRAM is scanned out by hardware.

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
