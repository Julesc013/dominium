/*
FILE: source/domino/render/soft/d_gfx_soft.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/d_gfx_soft
RESPONSIBILITY: Defines internal contract for `d_gfx_soft`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_GFX_SOFT_H
#define D_GFX_SOFT_H

#include "domino/gfx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_gfx_backend_soft_s {
    int  (*init)(void);
    void (*shutdown)(void);
    void (*submit_cmd_buffer)(const d_gfx_cmd_buffer *buf);
    void (*present)(void);
} d_gfx_backend_soft;

/* Registration for dispatcher */
const d_gfx_backend_soft *d_gfx_soft_register_backend(void);
void d_gfx_soft_set_framebuffer_size(i32 w, i32 h);
const u32* d_gfx_soft_get_framebuffer(i32* out_w, i32* out_h, i32* out_pitch_bytes);

#ifdef __cplusplus
}
#endif

#endif /* D_GFX_SOFT_H */
