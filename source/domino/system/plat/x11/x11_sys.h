/*
FILE: source/domino/system/plat/x11/x11_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/x11/x11_sys
RESPONSIBILITY: Implements `x11_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_X11_SYS_H
#define DOMINO_X11_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <dirent.h>
#include <sys/types.h>
#include <unistd.h>

typedef struct x11_global_t {
    Display* display;
    int      screen;
    Atom     wm_delete_window;
    Atom     net_wm_state;
    Atom     net_wm_state_fullscreen;
} x11_global_t;

struct dsys_window_t {
    Display*         display;
    int              screen;
    Window           window;
    Atom             wm_delete_window;
    Atom             net_wm_state;
    Atom             net_wm_state_fullscreen;
    int32_t          width;
    int32_t          height;
    int32_t          last_x;
    int32_t          last_y;
    dsys_window_mode mode;
    struct dsys_window_t* next;
};

struct dsys_dir_iter_t {
    DIR*  dir;
    char  base[260];
};

struct dsys_process_t {
    pid_t pid;
};

const dsys_backend_vtable* dsys_x11_get_vtable(void);

#endif /* DOMINO_X11_SYS_H */
