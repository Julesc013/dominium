# Renderer API (domino_gfx)

Public header: `include/domino/gfx.h`  
Core code: `source/domino/render/api/domino_gfx_core.c`  
Software backend: `source/domino/render/soft/**`

## ABI (dgfx_*) snapshot
- Versioned `dgfx_device_desc` selects backend (`DEFAULT/SOFTWARE/NULL/EXTERNAL`), size, format, and present mode; `dgfx_create_device`/`dgfx_destroy_device` own an opaque device on top of a `dsys_context`.
- Frame control remains minimal: `dgfx_begin_frame`/`dgfx_end_frame` plus `dgfx_resize` for swapchain size changes.
- `dgfx_get_canvas` hands back a `dom_canvas` handle representing the render target; the immediate IR stays canvas-centric for now.
- Backend selection is deferred to the descriptor; everything is stubbed to succeed without real GPU/platform work.

## Surface
- Opaque `domino_gfx_device`, optional `domino_gfx_texture`, `domino_gfx_font`.
- `domino_gfx_desc`: backend (AUTO/SOFT/GL*/DX*/VK/METAL), profile hint (TINY/FIXED/PROGRAMMABLE), width/height, fullscreen, vsync, framebuffer pixel format.
- Lifecycle: `domino_gfx_create_device(domino_sys_context*, const domino_gfx_desc*, domino_gfx_device**)`, `domino_gfx_destroy_device`.
- Frame: `domino_gfx_begin_frame`, `domino_gfx_end_frame`.
- Clear/2D: `domino_gfx_clear`, `domino_gfx_draw_filled_rect`.
- Textures: `domino_gfx_texture_create/destroy/update` (stubbed in soft backend).
- Blit/Text: `domino_gfx_draw_texture`, `domino_gfx_font_draw_text` (stubbed in soft backend).

## Backend selection
- `AUTO` currently resolves to `SOFT` for all platforms.
- GPU backends (GL/DX/VK/Metal) are TODO; API accepts them for future selection.

## Software backend
- Core: CPU framebuffer (A8R8G8B8) with clear + solid rect fill.
- Present targets:
  - Win32 GDI (`source/domino/render/soft/targets/win32/soft_target_win32.c`) uses `StretchDIBits` into a simple window.
  - Null target (`source/domino/render/soft/targets/null/soft_target_null.c`) for headless testing.
- Future targets (SDL/X11/VESA/etc.) stubbed as TODO; the interface is defined in `soft_internal.h`.

## Usage
Create a `domino_sys_context`, configure `domino_gfx_desc` (width/height/format), create device, then:
1. `domino_gfx_begin_frame`
2. `domino_gfx_clear` / `domino_gfx_draw_filled_rect` (and future draw calls)
3. `domino_gfx_end_frame`

The software backend always works; GPU backends will be added behind the same interface.

## Product usage
- Game (and visual tools) own the renderer; setup/launcher stay terminal/native-UI only. Launcher core does not depend on `domino_gfx`. Launcher CLI/TUI use `domino_term`, while a future GUI shell will hang off `domino_ui`/a thin UI layer separate from the game renderer.

## Minimal game startup example
```c
domino_sys_context* sys = NULL;
domino_sys_desc sdesc;
domino_gfx_device* gfx = NULL;
domino_gfx_desc gdesc;

sdesc.profile_hint = DOMINO_SYS_PROFILE_FULL;
domino_sys_init(&sdesc, &sys);

gdesc.backend = DOMINO_GFX_BACKEND_AUTO;
gdesc.profile_hint = DOMINO_GFX_PROFILE_FIXED;
gdesc.width = 640; gdesc.height = 360;
gdesc.fullscreen = 0; gdesc.vsync = 0;
gdesc.framebuffer_fmt = DOMINO_PIXFMT_A8R8G8B8;

domino_gfx_create_device(sys, &gdesc, &gfx);
domino_gfx_begin_frame(gfx);
domino_gfx_clear(gfx, 0.0f, 0.0f, 0.2f, 1.0f);
domino_gfx_end_frame(gfx);
domino_gfx_destroy_device(gfx);
domino_sys_shutdown(sys);
```
