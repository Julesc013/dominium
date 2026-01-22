# APR2 Extension Audit

Audit scope: platform runtime extensions, event queue/timing (APR1), renderer
backends, window creation path, and optional tool UIs.

## Platform runtime extension mechanism (APR0)
- `dsys_query_extension(name, version)` in `engine/include/domino/sys.h`
- Extension names (v1): `dsys.window_ex`, `dsys.error`, `dsys.cliptext`,
  `dsys.cursor`, `dsys.dragdrop`, `dsys.gamepad`, `dsys.power`
- `dsys_window_ex_api_v1` exposes show/hide/state/framebuffer size/DPI scale
- Extension vtables for clipboard/cursor/dragdrop/gamepad/power exist but are
  placeholder structs with reserved fields and no functions

## Event queue + timing (APR1)
- Single FIFO event queue with timestamps (`dsys_event.timestamp_us`)
- `dsys_inject_event()` for internal/TUI sources
- No per-window identity in `dsys_event` (multi-window routing missing)
- Deterministic vs interactive timing defined in `docs/app/TIMING_AND_CLOCKS.md`

## Renderer registry + backends (APR0)
- Backends: `soft` + `null` are implemented
- `dx9`/`dx11`/`gl2`/`vk1`/`metal` are compiled as stubs and map to `null`
- Explicit selection of stubbed backends currently succeeds but uses `null`
  (no explicit “unavailable” failure)

## Window creation path
- Client windowed mode uses `dsys_window_create`/`dsys_window_show`
- Renderer binds a native surface via `d_gfx_bind_surface`
- Platform runtime owns window creation; renderer does not create windows

## Tool UIs
- Tools offer optional TUI (`tools --tui`); CLI remains primary for tests
- GUI/other UI assets exist under `tools/**/ui` but are not required for CLI

## Extension status by platform/backend

### Win32 backend (`engine/modules/system/dsys_window_winnt.c`)
- DPI: implemented (`WM_DPICHANGED`, `dsys_window_get_dpi_scale`,
  `dsys_window_get_framebuffer_size`)
- Text input: `WM_CHAR` -> `DSYS_EVENT_TEXT_INPUT`
- Window modes: windowed/borderless/fullscreen best-effort in
  `dsys_window_set_mode`
- Cursor/clipboard/relative mouse: no public extension implementation yet
- IME: API exists but stubbed (no composition events)

### Non-Win32 builds (default to null backend)
- Windowing: null backend only (no real window)
- DPI: `dsys_window_get_dpi_scale` returns `1.0f`, no DPI change events
- Text input: no platform events; only injected events are available
- Cursor/clipboard/relative mouse: unsupported
- Window modes: struct-level mode only, no OS transitions

## Multi-window readiness
- `dsys_window_create` allows multiple window objects, but event queue has no
  window identity and `d_system_present_framebuffer` uses a global handle.
- Renderer binding (`d_gfx_bind_surface`) stores a single `g_native_window`.

## Gaps to address in APR2
- Define functional extension vtables for DPI/cursor/clipboard/text input/IME
  and window modes (versioned, optional).
- Add window identity to `dsys_event` for per-window routing.
- Make software present path multi-window aware or explicitly per-surface.
- Ensure explicit renderer selection fails loudly for unavailable GPU backends.
