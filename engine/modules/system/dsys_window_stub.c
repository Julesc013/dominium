/*
FILE: source/domino/system/dsys_window_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_window_stub
RESPONSIBILITY: Implements `dsys_window_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/system/dsys.h"
#include "dsys_internal.h"

#include <stdlib.h>
#include <string.h>

dsys_window* dsys_window_create(const dsys_window_desc* desc) {
    dsys_window* win;
    dsys_window_desc local;

    if (desc) {
        local = *desc;
    } else {
        local.x = 0;
        local.y = 0;
        local.width = 0;
        local.height = 0;
        local.mode = DWIN_MODE_WINDOWED;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->width = local.width;
    win->height = local.height;
    win->mode = local.mode;
    return win;
}

void dsys_window_destroy(dsys_window* win) {
    if (!win) {
        return;
    }
    free(win);
}

int dsys_window_should_close(dsys_window* win) {
    (void)win;
    return 1;
}

void dsys_window_present(dsys_window* win) {
    (void)win;
}

void dsys_window_get_size(dsys_window* win, int32_t* out_w, int32_t* out_h) {
    if (!win) {
        if (out_w) *out_w = 0;
        if (out_h) *out_h = 0;
        return;
    }
    if (out_w) *out_w = win->width;
    if (out_h) *out_h = win->height;
}
