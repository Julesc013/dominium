/*
FILE: source/domino/system/plat/cpm86/cpm86_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/cpm86/cpm86_sys
RESPONSIBILITY: Defines internal contract for `cpm86_sys`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_CPM86_SYS_H
#define DOMINO_CPM86_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <stdint.h>

struct cpm86_fb {
    uint8_t* pixels;
    uint16_t width;
    uint16_t height;
    uint16_t pitch;
    uint8_t  bpp;
};

struct dsys_window_t {
    struct cpm86_fb  fb;
    dsys_window_mode mode;
};

struct dsys_dir_iter_t {
    int dummy;
};

struct dsys_process_t {
    int dummy;
};

typedef struct cpm86_global_t {
    int          initialized;
    dsys_window* main_window;
    uint64_t     time_us;
    dsys_event   event_queue[16];
    int          ev_head;
    int          ev_tail;
} cpm86_global_t;

extern cpm86_global_t g_cpm86;

const dsys_backend_vtable* dsys_cpm86_get_vtable(void);

#endif /* DOMINO_CPM86_SYS_H */
