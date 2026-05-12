/*
FILE: source/domino/render/soft/soft_internal.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/soft_internal
RESPONSIBILITY: Defines internal contract for `soft_internal`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_SOFT_INTERNAL_H
#define DOMINO_SOFT_INTERNAL_H

#include "domino/gfx.h"

typedef struct domino_soft_target_ops {
    const char* name;
    int  (*init)(domino_sys_context* sys, int width, int height, domino_pixfmt fmt, void** out_state);
    void (*shutdown)(void* state);
    int  (*present)(void* state, const void* pixels, int width, int height, int stride_bytes);
} domino_soft_target_ops;

const domino_soft_target_ops* domino_soft_target_win32(void);
const domino_soft_target_ops* domino_soft_target_null(void);

int  domino_gfx_soft_create(domino_sys_context* sys,
                            const domino_gfx_desc* desc,
                            domino_gfx_device** out_dev);

#endif /* DOMINO_SOFT_INTERNAL_H */
