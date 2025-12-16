/*
FILE: source/domino/system/plat/wayland/wayland_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/wayland/wayland_sys
RESPONSIBILITY: Defines internal contract for `wayland_sys`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_WAYLAND_SYS_H
#define DOMINO_WAYLAND_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>
#include <sys/types.h>

struct wl_display;
struct wl_registry;
struct wl_compositor;
struct wl_surface;
struct xdg_wm_base;
struct xdg_surface;
struct xdg_toplevel;
struct wl_shell;
struct wl_shell_surface;
struct wl_seat;
struct wl_keyboard;
struct wl_pointer;

struct dsys_window_t {
    struct wl_surface*        surface;
    struct xdg_surface*       xdg_surface;
    struct xdg_toplevel*      xdg_toplevel;
    struct wl_shell_surface*  shell_surface;
    int32_t                   width;
    int32_t                   height;
    int32_t                   last_x;
    int32_t                   last_y;
    dsys_window_mode          mode;
};

struct dsys_dir_iter_t {
    DIR*  dir;
    char  base[260];
};

struct dsys_process_t {
    pid_t pid;
};

typedef struct wayland_global_t {
    int                    initialized;
    struct wl_display*     display;
    struct wl_registry*    registry;
    struct wl_compositor*  compositor;
    struct xdg_wm_base*    xdg_wm_base;
    struct wl_shell*       wl_shell;
    int                    use_xdg_shell;
    struct wl_seat*        seat;
    struct wl_keyboard*    keyboard;
    struct wl_pointer*     pointer;
    struct dsys_window_t*  main_window;
    dsys_event             event_queue[64];
    int                    event_head;
    int                    event_tail;
} wayland_global_t;

extern wayland_global_t g_wayland;

const dsys_backend_vtable* dsys_wayland_get_vtable(void);

#endif /* DOMINO_WAYLAND_SYS_H */
