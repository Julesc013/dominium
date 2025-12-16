/*
FILE: source/domino/system/plat/win16/win16_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/win16/win16_sys
RESPONSIBILITY: Implements `win16_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_WIN16_SYS_H
#define DOMINO_WIN16_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <windows.h>

struct dsys_window_t {
    HWND             hwnd;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
};

typedef struct win16_global_t {
    HINSTANCE hInstance;
    HWND      hwnd;
    int       class_registered;
    int       running;
} win16_global_t;

extern win16_global_t g_win16;

struct dsys_dir_iter_t {
    HANDLE          handle;
    WIN32_FIND_DATA data;
    int             first_pending;
    char            pattern[260];
};

struct dsys_process_t {
    int unused;
};

const dsys_backend_vtable* dsys_win16_get_vtable(void);

#endif /* DOMINO_WIN16_SYS_H */
