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

## SDL1 Backend
- API: SDL 1.2 (video, events, timer).
- Target systems: SDL1-era Windows 9x/XP, older Linux/macOS builds.
- UI modes: GUI (`ui_modes = 1`); windows and mouse supported, processes are stubbed.
- Features: single-window SDL_SetVideoMode surface (native handle is `SDL_Surface*`), fullscreen/borderless via SDL flags, SDL_PollEvent translation (quit, resize, key, mouse move/button/wheel), timers from SDL_GetTicks/SDL_Delay, stdio-backed file IO and `_findfirst`/`dirent` directory iteration.
- Limitations: single window, coarse millisecond timer, minimal text input, process spawning unimplemented.
- Build: enable with `-DDOMINO_USE_SDL1_BACKEND=ON` (alias `-DDSYS_BACKEND_SDL1=ON`) to compile `DSYS_BACKEND_SDL1` and link against SDL 1.2.

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

## POSIX Headless Backend
- API: POSIX (monotonic clocks, nanosleep, stdio file IO, dirent, fork/execvp), no native GUI.
- Target systems: Unix/Linux/BSD servers and headless nodes (CI, batch, simulation).
- UI modes: CLI/TUI only (`ui_modes = 0`); `has_windows = false`; no mouse/gamepad.
- Features: monotonic microsecond timer with `clock_gettime` (fallback `gettimeofday`), `nanosleep` for delays, XDG-based user data/config/cache paths (home fallback), `/proc/self/exe`→dir for app root (fallback `getcwd`), temp from `$TMPDIR` or `/tmp`, stdio-backed files, POSIX directory iteration, and `fork/execvp` + `waitpid` processes.
- Events/Windows: `dsys_window_create` returns `NULL`; window setters/getters are no-ops; `dsys_poll_event` always returns `false`.
- Build: enable with `-DDOMINO_USE_POSIX_BACKEND=ON` (alias `-DDSYS_BACKEND_POSIX=ON`) to compile `DSYS_BACKEND_POSIX` and include `source/domino/system/plat/posix/posix_sys.c`.

## Cocoa Backend (macOS)
- API: AppKit / Cocoa with Objective-C bridge; macOS 10.9+ (Intel + Apple Silicon).
- UI modes: GUI (`ui_modes = 1`); windows and mouse supported, high-res timer via `clock_gettime`/`mach_absolute_time`.
- Features: initializes `NSApplication` once, creates `NSWindow` objects and forwards AppKit events (resize, key up/down + text input, mouse move/button/wheel, close→quit), stdio-backed file IO, POSIX dirent iteration, and POSIX `fork/execvp` processes.
- Paths: app root from `_NSGetExecutablePath` + `realpath`; user data/config under `~/Library/Application Support/dominium/{data,config}`; cache under `~/Library/Caches/dominium`; temp from `_CS_DARWIN_USER_TEMP_DIR`, `$TMPDIR`, or `/tmp`.
- Build: enable with `-DDOMINO_USE_COCOA_BACKEND=ON` (alias `-DDSYS_BACKEND_COCOA=ON`) to compile `DSYS_BACKEND_COCOA`, add `source/domino/system/plat/cocoa/cocoa_sys.c` and `.m`, and link against AppKit.
- Limitations: fullscreen toggling is best-effort; text input buffer truncates to 7 UTF-8 bytes.
