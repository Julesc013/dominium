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

## DOS32 Backend (Fullscreen GUI/GFX)
- Target: MS-DOS 5/6.x with a 32-bit extender (DOS4GW, CWSDPMI/DJGPP runtime, etc.), real hardware or emulators.
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for a single logical fullscreen window; mouse optional, no gamepad; timers are coarse (`clock()` based).
- Windowing: tracks width/height/mode only; native handle is the `dsys_window*`; no OS window manager or mode switching here (renderer chooses VGA/VESA/CGA/etc.).
- Events: keyboard via `kbhit/getch` (ESC also yields a quit event); optional mouse can be added via INT 33h later; events buffered in a small ring.
- Filesystem/Paths: stdio-backed file IO, `dirent` directory iteration; paths resolve relative to `getcwd` with `DATA/`, `CONFIG/`, `CACHE/`, and `TEMP/` under the current directory; DOS 8.3 filenames apply.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDOMINO_USE_DOS32_BACKEND=ON` (alias `-DDSYS_BACKEND_DOS32=ON`) to compile `source/domino/system/plat/dos32/dos32_sys.c`.
- Renderer note: DOS32 dsys only reports the logical framebuffer size; dgfx backends pick the actual video mode and framebuffer.

## DOS16 Backend (Fullscreen GUI/GFX)
- Target: MS-DOS 3.x-6.x, 16-bit real mode builds (tiny/medium/large memory models) on classic compilers.
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for one logical fullscreen surface; no mouse/gamepad; coarse timer only.
- Windowing: tracks logical width/height/mode; always fullscreen; native handle is the `dsys_window*` (no OS window object), renderer chooses VGA/EGA/CGA/VESA mode changes.
- Events: keyboard via `kbhit/getch`; ESC also yields a quit event; key-up is synthesized immediately after key-down; no OS window close events and mouse is not implemented.
- Time/Delay: uses `clock()` ticks converted to microseconds; `sleep_ms` busy-waits on the coarse clock.
- Filesystem/Paths: stdio file IO; `dirent` directory iteration; paths are relative to `getcwd` with `DATA/`, `CONFIG/`, `CACHE/`, and `TEMP/` folders (8.3 filenames expected).
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDOMINO_USE_DOS16_BACKEND=ON` (alias `-DDSYS_BACKEND_DOS16=ON`) to compile `source/domino/system/plat/dos16/dos16_sys.c`.
- Renderer note: dsys reports only logical framebuffer size; dgfx DOS VGA/CGA/EGA/VESA backends own mode switching and framebuffer pointers.

## Win16 Backend (GUI/GFX)
- Target: Windows 3.x (real/standard/386 enhanced), Win16 API (user.dll/gdi.dll), ANSI strings only.
- UI modes: GUI (`ui_modes = 1`); `has_windows = true`, mouse supported, no gamepad, coarse timer only.
- Windowing: registers a `DominoWin16` class and creates one top-level ANSI window (`HWND` stored in `dsys_window`); simulates fullscreen via popup + screen-sized `MoveWindow`; one window only.
- Events: translates `WM_CLOSE`→quit, `WM_KEYDOWN/UP`, `WM_MOUSEMOVE`, `WM_LBUTTONDOWN/UP`, `WM_RBUTTONDOWN/UP`, and `WM_SIZE` to `dsys_event`; small ring buffer drained after `PeekMessage`/`DispatchMessage`.
- Time/Delay: `GetTickCount()` converted to microseconds (wrap ~49 days); `sleep_ms` spins on the coarse tick (best-effort yield).
- Paths/FS: ANSI paths; app root from `GetModuleFileName` (fallback `.`); user data/config/cache under `./DOMINIUM/{DATA,CONFIG,CACHE}`; temp from `GetTempPath`/`TEMP`/`.`; stdio file IO; directory iteration via `FindFirst`/`FindNext` data.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Limitations: no Unicode, cooperative multitasking, no true exclusive fullscreen.

## Cocoa Backend (macOS)
- API: AppKit / Cocoa with Objective-C bridge; macOS 10.9+ (Intel + Apple Silicon).
- UI modes: GUI (`ui_modes = 1`); windows and mouse supported, high-res timer via `clock_gettime`/`mach_absolute_time`.
- Features: initializes `NSApplication` once, creates `NSWindow` objects and forwards AppKit events (resize, key up/down + text input, mouse move/button/wheel, close→quit), stdio-backed file IO, POSIX dirent iteration, and POSIX `fork/execvp` processes.
- Paths: app root from `_NSGetExecutablePath` + `realpath`; user data/config under `~/Library/Application Support/dominium/{data,config}`; cache under `~/Library/Caches/dominium`; temp from `_CS_DARWIN_USER_TEMP_DIR`, `$TMPDIR`, or `/tmp`.
- Build: enable with `-DDOMINO_USE_COCOA_BACKEND=ON` (alias `-DDSYS_BACKEND_COCOA=ON`) to compile `DSYS_BACKEND_COCOA`, add `source/domino/system/plat/cocoa/cocoa_sys.c` and `.m`, and link against AppKit.
- Limitations: fullscreen toggling is best-effort; text input buffer truncates to 7 UTF-8 bytes.
