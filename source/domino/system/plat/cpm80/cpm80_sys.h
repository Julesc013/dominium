/*
FILE: source/domino/system/plat/cpm80/cpm80_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/cpm80/cpm80_sys
RESPONSIBILITY: Implements `cpm80_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_CPM80_SYS_H
#define DOMINO_CPM80_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <stdint.h>

struct cpm80_fb {
    uint8_t* pixels;
    uint16_t width;
    uint16_t height;
    uint16_t pitch;
    uint8_t  bpp;
};

struct dsys_window_t {
    struct cpm80_fb   fb;
    dsys_window_mode  mode;
};

struct dsys_dir_iter_t {
    int dummy;
};

struct dsys_process_t {
    int dummy;
};

typedef struct cpm80_global_t {
    int           initialized;
    dsys_window*  main_window;
    uint64_t      time_us;
    dsys_event    event_queue[16];
    int           ev_head;
    int           ev_tail;
} cpm80_global_t;

extern cpm80_global_t g_cpm80;

const dsys_backend_vtable* dsys_cpm80_get_vtable(void);

#endif /* DOMINO_CPM80_SYS_H */
