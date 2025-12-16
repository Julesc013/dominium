/*
FILE: source/domino/system/plat/dos32/dos32_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/dos32/dos32_sys
RESPONSIBILITY: Implements `dos32_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DOS32_SYS_H
#define DOMINO_DOS32_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>

/* DOS32 fullscreen window representation */
struct dsys_window_t {
    void*            framebuffer; /* linear framebuffer pointer */
    int32_t          width;
    int32_t          height;
    int32_t          pitch;       /* bytes per scanline */
    int32_t          bpp;         /* bits per pixel */
    dsys_window_mode mode;        /* fullscreen only */
};

/* processes are unsupported on DOS */
struct dsys_process_t {
    int dummy;
};

/* directory iterator backed by DIR* (DJGPP provides dirent) */
struct dsys_dir_iter_t {
    DIR* dir;
};

typedef struct dos32_global_t {
    int           initialized;
    struct dsys_window_t* main_window;

    /* VESA / framebuffer information */
    uint16_t      vesa_mode;
    void*         lfb;
    uint32_t      lfb_size;
    uint32_t      pitch;
    int32_t       fb_width;
    int32_t       fb_height;
    int32_t       fb_bpp;

    /* input state */
    int32_t mouse_x;
    int32_t mouse_y;
    int     mouse_buttons;

    dsys_event event_queue[32];
    int        ev_head;
    int        ev_tail;
} dos32_global_t;

extern dos32_global_t g_dos32;

const dsys_backend_vtable* dsys_dos32_get_vtable(void);

#endif /* DOMINO_DOS32_SYS_H */
