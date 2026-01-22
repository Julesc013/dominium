# Platform Runtime Interface (DSYS)

This document describes the platform/runtime interface exposed by `dsys_*`.
It is the only layer that touches OS integration (windowing, time, filesystem,
process), and higher layers must not call OS APIs directly.

## Scope
- OS lifecycle: `dsys_init`, `dsys_shutdown`, `dsys_get_caps`
- Window lifecycle and state (no renderer-specific logic)
- Event polling (no callbacks into game logic)
- Monotonic time and sleep
- Filesystem and process helpers
- Raw input + IME (no semantic mapping)

## Versioning
- ABI vtables: `dsys_*_api_v1` structs in `engine/include/domino/sys.h`
- Interface IDs: `DSYS_IID_*` constants
- Extensions: `dsys_query_extension(name, version)` (versioned by integer)

## Core API
- `dsys_init`/`dsys_shutdown` initialize the compiled platform backend
- `dsys_get_caps` reports capability flags (best-effort)
- `dsys_time_now_us` is monotonic when available
- `dsys_sleep_ms` is best-effort wall sleep

## Window API
- Create/destroy: `dsys_window_create`, `dsys_window_destroy`
- Mode/size: `dsys_window_set_mode`, `dsys_window_set_size`, `dsys_window_get_size`
- Visibility: `dsys_window_show`, `dsys_window_hide`
- State query: `dsys_window_get_state` fills `dsys_window_state`
  - `should_close`, `focused`, `minimized`, `maximized`, `occluded`
- Surface: `dsys_window_get_native_handle`
- Framebuffer: `dsys_window_get_framebuffer_size`
- DPI: `dsys_window_get_dpi_scale` (best-effort)
- Identity: `dsys_window_get_id`

## Events
`dsys_poll_event` returns queued events only; no callbacks are used.
Event types include:
- `DSYS_EVENT_WINDOW_RESIZED`
- `DSYS_EVENT_DPI_CHANGED` (payload: `scale`)
- Keyboard/mouse/gamepad input events (raw)
Each event includes `window`/`window_id` for per-window routing when applicable.

Raw input is available via `dsys_input_poll_raw`. IME is exposed via
`dsys_ime_start`, `dsys_ime_stop`, `dsys_ime_set_cursor`, `dsys_ime_poll`.

## Error model
- Return codes are `dsys_result` where applicable
- `dsys_last_error_code`/`dsys_last_error_text` return the last failure
- Error state is cleared on entry to public API calls

## Extensions
`dsys_query_extension(name, 1)` returns a versioned vtable or NULL.
Known extensions:
- `dsys.window_ex` -> `dsys_window_ex_api_v1` (show/hide/state/framebuffer/DPI)
- `dsys.dpi` -> alias of `dsys.window_ex`
- `dsys.window_mode` -> `dsys_window_mode_api_v1`
- `dsys.text_input` -> `dsys_text_input_api_v1` (IME hooks may be stubbed)
- `dsys.error` -> `dsys_error_api_v1`
- `dsys.cliptext` -> `dsys_cliptext_api_v1` (Win32 implemented; others stubbed)
- `dsys.cursor` -> `dsys_cursor_api_v1` (Win32 implemented; others stubbed)
- `dsys.dragdrop` -> `dsys_dragdrop_api_v1` (stubbed)
- `dsys.gamepad` -> `dsys_gamepad_api_v1` (stubbed)
- `dsys.power` -> `dsys_power_api_v1` (stubbed)

## Backend selection
- One platform backend is compiled per build; no dynamic loading yet
- `dom_dsys_register_caps_backends` registers the compiled backend in caps
- `dom_sys_select_backend` only accepts the compiled backend name; otherwise it
  fails loudly (no silent fallback for explicit requests)
