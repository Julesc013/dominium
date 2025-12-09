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

## Wayland Backend
- Target: Linux/BSD systems running a Wayland compositor (GNOME/KDE/sway/etc.), single display/seat/window model for v1.
- UI modes: GUI (`ui_modes = 1`); real `wl_surface` + `xdg_toplevel` (preferred) or `wl_shell_surface`, mouse/keyboard supported, high-res timer via `clock_gettime`.
- Events: wl_seat keyboard/pointer listeners feed a 64-slot ring; key down/up, mouse move/button/wheel, resize from configure, close → quit via `xdg_toplevel` close; `dsys_poll_event` pumps `wl_display_dispatch_pending` then drains the queue.
- Windowing: creates one toplevel surface, fullscreen toggled with `xdg_toplevel_set_fullscreen`; native handle returns the `wl_surface*`.
- Paths/FS: POSIX stdio + dirent; paths from `/proc/self/exe` (fallback `getcwd`), XDG data/config/cache with `/dominium` suffix, temp from `$TMPDIR` or `/tmp`.
- Processes: POSIX `fork/execvp` + `waitpid`.
- Build: enable with `-DDOMINO_USE_WAYLAND_BACKEND=ON` (alias `-DDSYS_BACKEND_WAYLAND=ON`), compile `source/domino/system/plat/wayland/wayland_sys.c`, link against `wayland-client` (and system xdg-shell headers).

## POSIX Backend (Headless UNIX)
- API: POSIX (monotonic clocks, nanosleep, stdio file IO, dirent, fork/execvp); no native GUI or event loop.
- Target systems: Linux/BSD/Solaris/AIX/HP-UX/macOS headless servers, CI, containers, and other Unix-like builds without GUI.
- UI modes: CLI/TUI only (`ui_modes = 0`); `has_windows = false`; mouse/gamepad unsupported.
- Features: monotonic microsecond timer via `clock_gettime` (fallback `gettimeofday`), `nanosleep`, XDG data/config/cache roots under `dominium`, app root from `/proc/self/exe` dir (fallback `getcwd`), temp from `$TMPDIR` or `/tmp`, stdio-backed file IO, dirent iteration, and `fork/execvp` + `waitpid` processes.
- Events/Windows: window APIs are no-ops/return `NULL`; `dsys_poll_event` always returns `false` (no stdin polling by default).
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

## CP/M-80 Backend (Logical Fullscreen GUI/GFX)
- Target: CP/M-80 (8080/Z80) BDOS environments (CP/M, CP/M-Plus, compatibles).
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for a single logical fullscreen surface; no mouse/gamepad; coarse/synthetic timer (no high-res).
- Windowing: tracks logical width/height/mode only; always fullscreen; native handle is the `dsys_window*` (CP/M has no window manager); renderer maps this to terminal/video hardware and owns any framebuffer.
- Events: keyboard-only via BDOS function 6 with `E=0xFF` (non-blocking); ESC (0x1B) or CTRL+C (0x03) produce quit events; other keys emit key-down; no mouse.
- Time/Delay: uses `clock()` if present, otherwise a synthetic monotonic counter (adds ~1 ms per call); `sleep_ms` busy-waits on that counter.
- Filesystem/Paths: 8.3 uppercase filenames with drive/user semantics; logical paths map to the current drive (`A:` defaults) plus prefixes like `A:DOMDATA`, `A:DOMCFG`, `A:CACHE`, and `A:TEMP`; stdio-backed file IO only.
- Directory iteration: stubbed (iterator allocates but yields no entries); BDOS search-first/search-next can be layered in later.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDSYS_BACKEND_CPM80=ON` to compile `source/domino/system/plat/cpm80/cpm80_sys.c`; build with a CP/M-80 toolchain (z88dk, Hi-Tech C, Aztec C, etc.).
- Renderer note: the reported width/height are purely logical; dgfx backends decide how to draw (character grid, software framebuffer, custom hardware).

## CP/M-86 Backend (Logical Fullscreen GUI/GFX)
- Target: CP/M-86 1.x/2.x BDOS environments on 8086/80186/80286 hardware (classic Digital Research or compatible BIOS/BDOS).
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for a single logical fullscreen surface; no mouse/gamepad; coarse/synthetic timer (no high-res).
- Windowing: tracks logical width/height/mode only; always fullscreen; native handle is the `dsys_window*`; renderer supplies any real framebuffer/mode switching.
- Events: keyboard-only via BDOS function 6 with `E=0xFF` (non-blocking poll) or BIOS-compatible INT 16h; ESC (0x1B) or CTRL+C (0x03) yield quit events, other keys emit key-down.
- Time/Delay: uses `clock()` when available, otherwise a synthetic monotonic counter (+~1 ms per call); `sleep_ms` busy-waits on that counter.
- Filesystem/Paths: CP/M drive/user semantics with 8.3 uppercase names; logical paths map to `A:` roots such as `A:DOMDATA`, `A:DOMCFG`, `A:CACHE`, and `A:TEMP`; stdio-backed file IO; directory iteration is stubbed (flat filesystem, `is_dir = false`).
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDSYS_BACKEND_CPM86=ON` to compile `source/domino/system/plat/cpm86/cpm86_sys.c`; build with a CP/M-86 toolchain (Digital Research C, OpenWatcom-16 CP/M mode, etc.).
- Renderer note: identical logical semantics to CP/M-80/DOS backends—graphics are renderer-owned; dsys only reports the logical fullscreen size for deterministic behaviour.

## Win16 Backend (GUI/GFX)
- Target: Windows 3.x (real/standard/386 enhanced), Win16 API (user.dll/gdi.dll), ANSI strings only.
- UI modes: GUI (`ui_modes = 1`); `has_windows = true`, mouse supported, no gamepad, coarse timer only.
- Windowing: registers a `DominoWin16` class and creates one top-level ANSI window (`HWND` stored in `dsys_window`); simulates fullscreen via popup + screen-sized `MoveWindow`; one window only.
- Events: translates `WM_CLOSE`→quit, `WM_KEYDOWN/UP`, `WM_MOUSEMOVE`, `WM_LBUTTONDOWN/UP`, `WM_RBUTTONDOWN/UP`, and `WM_SIZE` to `dsys_event`; small ring buffer drained after `PeekMessage`/`DispatchMessage`.
- Time/Delay: `GetTickCount()` converted to microseconds (wrap ~49 days); `sleep_ms` spins on the coarse tick (best-effort yield).
- Paths/FS: ANSI paths; app root from `GetModuleFileName` (fallback `.`); user data/config/cache under `./DOMINIUM/{DATA,CONFIG,CACHE}`; temp from `GetTempPath`/`TEMP`/`.`; stdio file IO; directory iteration via `FindFirst`/`FindNext` data.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Limitations: no Unicode, cooperative multitasking, no true exclusive fullscreen.

## Cocoa Backend (macOS Modern GUI)
- API: AppKit / Cocoa bridge on macOS 10.9+ (Intel + Apple Silicon); runs NSApplication/NSWindow on the main thread only.
- UI modes: GUI (`ui_modes = 1`); real `NSWindow*` native handles for the renderer, windows/mouse supported, high-res timer via `mach_absolute_time`.
- Events: key up/down, mouse move/button/wheel, resize, and close→quit translated by an Objective-C delegate into a 128-slot ring buffer; `dsys_poll_event` pumps `[NSApp nextEventMatchingMask:untilDate:inMode:dequeue:]` non-blocking for deterministic delivery.
- Paths: UTF-8 paths; executable root from `NSBundle` executable path, user data/config under `~/Library/Application Support/dominium/{data,config}`, cache under `~/Library/Caches/dominium`, temp from `NSTemporaryDirectory`.
- Filesystem: stdio-backed file IO, POSIX dirent iteration; processes stubbed (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDOMINO_USE_COCOA_BACKEND=ON` (alias `-DDSYS_BACKEND_COCOA=ON`) to compile `source/domino/system/plat/cocoa/cocoa_sys.c/.h` plus `cocoa_sys_objc.m` and link against Cocoa/AppKit/Foundation.

## Carbon Backend (macOS Carbon GUI)
- API: Carbon Event/Window Manager + CoreServices; classic 32-bit Carbon (`WindowRef` native handle).
- Target systems: Mac OS X 10.0–10.6/10.7 where Carbon remains available (PPC/Intel).
- UI modes: GUI (`ui_modes = 1`); `has_windows = true`, mouse supported, high-res timer via `UpTime`/`AbsoluteToNanoseconds`.
- Windowing: creates Carbon document windows (`CreateNewWindow`); close→quit event; bounds-change→`DSYS_EVENT_WINDOW_RESIZED`; fullscreen/borderless sizes the window to the main display; native handle is the `WindowRef`.
- Events: Carbon event handlers translate mouse move/button/wheel, raw key down/up/repeat, and window close/resize into `dsys_event` via a small ring buffer; `dsys_poll_event` pumps `ReceiveNextEvent`/`SendEventToEventTarget` non-blocking before draining the queue.
- Time/Delay: monotonic microseconds from `UpTime` → `AbsoluteToNanoseconds`; `sleep_ms` busy-waits while optionally pumping Carbon events.
- Paths: app root from `CFBundleCopyBundleURL` (POSIX UTF-8 path, fallback `getcwd`); user data/config/cache from `FSFindFolder` Application Support/Preferences/CachedData + `/dominium`; temp from the user temporary folder or `/tmp`.
- Filesystem: stdio-backed file IO; dirent/stat directory iteration with UTF-8 POSIX paths.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDOMINO_USE_CARBON_BACKEND=ON` (alias `-DDSYS_BACKEND_CARBON=ON`) to compile `source/domino/system/plat/carbon/carbon_sys.c/.h` and link against the Carbon framework (32-bit Carbon targets).
