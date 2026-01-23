# Platform Extensions

`dsys_query_extension(name, version)` returns a vtable pointer or NULL. Version
is an integer; the current version is `1`.
Version macros are defined in `engine/include/domino/sys.h` as
`DSYS_EXTENSION_*_VERSION` and are printed in `--build-info`.

Availability rules:
- NULL return means the extension is unavailable.
- If the extension is present but an operation is unsupported, functions return
  `DSYS_ERR_UNSUPPORTED` and populate `dsys_last_error_text()`.

## Extensions (v1)

### dsys.window_ex
API: `dsys_window_ex_api_v1`
- show/hide, get_state, get_framebuffer_size, get_dpi_scale
- Status: Win32 implemented; other backends return defaults or unsupported.

### dsys.dpi
Alias of `dsys.window_ex` (DPI scale and DPI change events).

### dsys.window_mode
API: `dsys_window_mode_api_v1`
- set_mode (returns `DSYS_OK`/`DSYS_ERR_UNSUPPORTED`)
- get_mode
- Status: implemented; returns unsupported on headless backends.

### dsys.cursor
API: `dsys_cursor_api_v1`
- set_cursor, show_cursor, confine_cursor, set_relative_mode
- Status: Win32 implemented. Relative mode uses raw input best-effort; other
  platforms return unsupported.

### dsys.cliptext
API: `dsys_cliptext_api_v1`
- get_text, set_text (UTF-8)
- Status: Win32 implemented via CF_UNICODETEXT; other platforms return
  unsupported.

### dsys.text_input
API: `dsys_text_input_api_v1`
- start/stop, set_ime_cursor, poll_ime
- Status: interface present; IME composition is stubbed unless a backend
  implements it.

### dsys.error
API: `dsys_error_api_v1`

### dsys.dragdrop / dsys.gamepad / dsys.power
APIs present; stubbed in the current build.
