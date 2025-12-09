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
- UI modes: GUI (`ui_modes = 1`); windows and mouse supported, process spawning via OS APIs.
- Features: single-window SDL_SetVideoMode surface (native handle is `SDL_Surface*`), fullscreen/borderless via SDL flags, SDL_PollEvent translation (quit, resize, key, mouse move/button/wheel), timers from SDL_GetTicks/SDL_Delay (millisecond resolution), stdio-backed file IO, `FindFirstFile`/`dirent` directory iteration, and basic process spawn/wait (`CreateProcess` or `fork/execvp`).
- Limitations: single window, coarse millisecond timer, minimal text input.
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
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for a single logical fullscreen window; mouse supported when INT 33h driver is present; no gamepad; timers are coarse (`clock()`/`uclock()` based).
- Windowing: attempts to enter VESA 0x101 (640x480x8) with linear framebuffer mapping via `__dpmi_physical_address_mapping`; falls back to VGA mode 13h. `dsys_window` stores framebuffer pointer, pitch, width, height, and bpp; `window_get_native_handle` returns the framebuffer pointer for software renderers.
- Events: keyboard via `kbhit/getch` with synthesized key-up and ESC→quit; mouse move/button via INT 33h; 32-slot ring buffer drained by `dsys_poll_event`.
- Filesystem/Paths: stdio-backed file IO, `dirent` directory iteration; all `dsys_get_path` kinds map to `"."` (DOS 8.3 filenames expected).
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDOMINO_USE_DOS32_BACKEND=ON` (alias `-DDSYS_BACKEND_DOS32=ON`) to compile `source/domino/system/plat/dos32/dos32_sys.c`.
- Renderer note: use the returned framebuffer pointer/pitch to write pixels directly to the mapped LFB (or the fallback heap buffer when running hosted).

## DOS16 Backend (Fullscreen GUI/GFX)
- Target: MS-DOS 3.x-6.x, 16-bit real mode builds (tiny/medium/large memory models) on classic compilers.
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for one logical fullscreen surface; mouse supported if an INT 33h driver is present; no gamepad; coarse timer only.
- Windowing: switches to VGA mode 13h (320x200x8); `dsys_window` exposes a `dos16_fb_handle` (segment:offset, width/height/pitch/bpp, VESA flag). Native handle returns this framebuffer descriptor.
- Events: keyboard via `kbhit/getch`; ESC also yields a quit event; key-up is synthesized immediately after key-down; mouse move/button via INT 33h when available; no OS window close events.
- Time/Delay: uses `clock()` ticks converted to microseconds; `sleep_ms` busy-waits on the coarse clock.
- Filesystem/Paths: stdio file IO; `dirent` directory iteration; paths map to `"."` for all kinds.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDOMINO_USE_DOS16_BACKEND=ON` (alias `-DDSYS_BACKEND_DOS16=ON`) to compile `source/domino/system/plat/dos16/dos16_sys.c`.
- Renderer note: renderers use the returned framebuffer descriptor to write directly to 0xA000:0000 (mode 13h) or future VESA banked modes.

## CP/M-80 Backend (Logical Fullscreen GUI/GFX)
- Target: CP/M-80 (8080/Z80) BDOS environments (CP/M, CP/M-Plus, compatibles).
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for a single logical fullscreen surface; no mouse/gamepad; synthetic monotonic timer (no high-res).
- Windowing: allocates an in-RAM 320x200x8 framebuffer; native handle returns a `cpm80_fb*` (pixels pointer, width/height/pitch/bpp); always fullscreen.
- Events: keyboard-only via BDOS function 6 with `E=0xFF` (non-blocking); ESC (0x1B) produces quit events; other keys emit key-down; no mouse.
- Time/Delay: purely logical counter (`time_us`) advanced by `sleep_ms`.
- Filesystem/Paths: stdio-backed file IO; paths map to `""`/current drive for all `dsys_path_kind` values.
- Directory iteration: stubbed (iterator returns no entries); BDOS search-first/search-next can be layered in later.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDSYS_BACKEND_CPM80=ON` to compile `source/domino/system/plat/cpm80/cpm80_sys.c`; build with a CP/M-80 toolchain (z88dk, Hi-Tech C, Aztec C, etc.).
- Renderer note: the reported width/height are purely logical; dgfx backends decide how to draw (character grid, software framebuffer, custom hardware).

## CP/M-86 Backend (Logical Fullscreen GUI/GFX)
- Target: CP/M-86 1.x/2.x BDOS environments on 8086/80186/80286 hardware (classic Digital Research or compatible BIOS/BDOS).
- UI modes: GUI (`ui_modes = 1`); `has_windows = true` for a single logical fullscreen surface; no mouse/gamepad; synthetic monotonic timer (no high-res).
- Windowing: allocates an in-RAM 320x200x8 framebuffer; native handle is `cpm86_fb*` with pixels pointer and layout; always fullscreen.
- Events: keyboard-only via `kbhit/getch` when available; ESC (0x1B) yields quit, other keys emit key-down.
- Time/Delay: purely logical counter advanced by `sleep_ms`.
- Filesystem/Paths: CP/M drive/user semantics with 8.3 uppercase names; all `dsys_get_path` kinds map to the current drive (`""`).
- Directory iteration: stubbed (no entries); processes unsupported.
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

## Carbon Backend (Classic/Carbon GUI)
- API: Carbon Event/Window Manager + CoreServices; 32-bit Carbon (`WindowRef` native handle) for CarbonLib and early macOS.
- Target systems: Mac OS 8.6–9.2 with CarbonLib and Mac OS X 10.0–10.4+ (PPC/Intel) running Carbon apps.
- UI modes: GUI (`ui_modes = 1`); `has_windows = true`, mouse supported, high-res timer via `UpTime`/`AbsoluteToNanoseconds`.
- Windowing: creates Carbon document windows (`CreateNewWindow`); close→quit event; bounds-change→`DSYS_EVENT_WINDOW_RESIZED`; fullscreen/borderless approximated by sizing to the main display; native handle is the `WindowRef`.
- Events: `ReceiveNextEvent` pumps non-blocking; keyboard (raw down/up/repeat), mouse move/button/wheel, window close/resize, and HICommand/App quit translate directly into a 64-slot ring drained by `dsys_poll_event`.
- Time/Delay: monotonic microseconds from `UpTime` → `AbsoluteToNanoseconds`; `sleep_ms` uses `Delay` ticks (~60 Hz) while optionally pumping events.
- Paths: app root from `CFBundleCopyBundleURL` (POSIX UTF-8 path, fallback `getcwd`); user data/config/cache from `FSFindFolder` Application Support/Preferences/CachedData + `/dominium`; temp from the user temporary folder or `/tmp`.
- Filesystem: stdio-backed file IO; dirent iteration with best-effort `is_dir` flag.
- Processes: unsupported (`spawn` returns `NULL`, `wait` returns `-1`).
- Build: enable with `-DDOMINO_USE_CARBON_BACKEND=ON` (alias `-DDSYS_BACKEND_CARBON=ON`) to compile `source/domino/system/plat/carbon/carbon_sys.c/.h` and link against the Carbon framework (32-bit Carbon targets).
