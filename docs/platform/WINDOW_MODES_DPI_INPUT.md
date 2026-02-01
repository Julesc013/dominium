Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Window Modes, DPI, and Input

## Coordinate spaces
- Logical window size: `dsys_window_get_size`.
- Framebuffer size: `dsys_window_get_framebuffer_size` (logical size scaled by
  DPI where available).
- DPI scale: `dsys_window_get_dpi_scale` (best-effort); DPI changes emit
  `DSYS_EVENT_DPI_CHANGED` with `payload.dpi.scale`.

## Window modes
- Modes: `DWIN_MODE_WINDOWED`, `DWIN_MODE_BORDERLESS`, `DWIN_MODE_FULLSCREEN`.
- Set mode: `dsys_window_set_mode` (best-effort).
- Extension: `dsys.window_mode` provides `set_mode` with explicit
  success/failure reporting.
- Win32 behavior:
  - Borderless: `WS_POPUP` style.
  - Fullscreen: resizes to display bounds (best-effort, not exclusive).
- Headless backends return `DSYS_ERR_UNSUPPORTED` for mode transitions.

## Input and text
- Key events: `DSYS_EVENT_KEY_DOWN`/`DSYS_EVENT_KEY_UP` (raw keycodes).
- Text input: `DSYS_EVENT_TEXT_INPUT` is distinct from key events.
- IME hooks: `dsys.text_input` extension + `dsys_ime_*` functions; currently
  stubbed unless a platform backend implements composition.
- Relative mouse: `dsys.cursor` provides `set_relative_mode`; Win32 uses raw
  input best-effort and emits `dx`/`dy` in `DSYS_EVENT_MOUSE_MOVE`.