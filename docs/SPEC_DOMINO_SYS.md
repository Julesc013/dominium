# Domino System Stub (dsys_)

Public header: `include/domino/sys.h`  
Stub implementation: `source/domino/system/sys.c`

This pass wires up a portable, deterministic stub backend. It exposes the full dsys_* surface so the engine can build and run without real OS hooks. Platform backends (win32, sdl2, x11, dos, etc.) will later live in platform-specific directories and replace this stub.

## API surface
- Lifecycle: `dsys_init` → `DSYS_OK`, `dsys_shutdown` no-op, `dsys_get_caps` returns `{ name = "stub", ui_modes = 0, has_windows/mouse/gamepad/high_res_timer = false }`.
- Time: `dsys_time_now_us` uses `clock()` ticks converted to microseconds; `dsys_sleep_ms` uses `Sleep`/`nanosleep` where available, otherwise a spin wait.
- Window: `dsys_window_create/destroy/set_mode/set_size/get_size/get_native_handle` manage an in-memory handle (x/y/size/mode only); native handle is always `NULL`.
- Events: `dsys_poll_event` clears the output and always returns `false` (empty queue).
- Paths: `dsys_get_path` returns `"."` for all `dsys_path_kind` values.
- Files: `dsys_file_open/read/write/seek/tell/close` wrap stdio with a `void*` handle.
- Directories: `dsys_dir_open` returns `NULL`, `dsys_dir_next` returns `false` and zeroes its output, `dsys_dir_close` is a no-op.
- Processes: `dsys_process_spawn` returns `NULL`, `dsys_process_wait` returns `-1`, `dsys_process_destroy` is a no-op.

## Notes
- Header stays platform-agnostic; sys.c only uses small `#if defined(_WIN32)` / `_POSIX_VERSION` guards.
- Behaviour is deterministic and side-effect free so other layers can safely call into it until real backends land.

## SDL2 Backend
- API: SDL2 (video, events, timer).
- Target systems: any platform with SDL2 available (Windows, macOS, Linux, BSD).
- UI modes: GUI (`ui_modes = 1`); windows and mouse supported, processes are stubbed.
- Features: creates real SDL windows, forwards SDL events to `dsys_event`, high-resolution timers via `SDL_GetPerformanceCounter`, filesystem and directory iteration via stdio/OS calls.
- Limitations: process spawning is unimplemented (returns `NULL`/`-1`), path resolution relies on `SDL_GetBasePath` and `SDL_GetPrefPath`, and native handles are `SDL_Window*`.
- Build: enable with `-DDOMINO_USE_SDL2_BACKEND=ON` to compile `DSYS_BACKEND_SDL2` and link against SDL2.

## X11 Backend
- API: Xlib + POSIX (time, filesystem, dirent, fork/exec).
- Target systems: Unix/Linux/BSD with an X11 server available.
- UI modes: GUI (`ui_modes = 1`); windows/mouse supported, gamepads unimplemented.
- Features: creates X11 windows, translates core X11 events (resize, key, mouse, wheel, WM_DELETE_WINDOW→quit), uses monotonic clocks for microsecond timing, stdio-based file IO, POSIX directory iteration, and `fork/execvp` process spawning. Native window handle is the X11 `Window` ID.
- Paths: app root from `/proc/self/exe` (fallback `getcwd`), user data/config/cache from XDG base dirs (`$XDG_*` or `$HOME/.local/share|.config|.cache` + `/dominium`), temp from `$TMPDIR` or `/tmp`.
- Limitations: fullscreen/borderless is best-effort via EWMH `_NET_WM_STATE_FULLSCREEN`; text input is minimal; requires a running display connection.
- Build: enable with `-DDOMINO_USE_X11_BACKEND=ON` to compile `DSYS_BACKEND_X11`, add `source/domino/system/plat/x11/x11_sys.c`, and link against X11.
