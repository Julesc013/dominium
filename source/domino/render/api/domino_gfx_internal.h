/*
FILE: source/domino/render/api/domino_gfx_internal.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/domino_gfx_internal
RESPONSIBILITY: Implements `domino_gfx_internal`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_GFX_INTERNAL_H
#define DOMINO_GFX_INTERNAL_H

#include "domino/gfx.h"
#include "domino/sys.h"

typedef struct domino_gfx_backend_vtable {
    void (*destroy)(domino_gfx_device*);
    int  (*begin_frame)(domino_gfx_device*);
    int  (*end_frame)(domino_gfx_device*);
    int  (*clear)(domino_gfx_device*, float, float, float, float);
    int  (*draw_rect)(domino_gfx_device*, const domino_gfx_rect*, float, float, float, float);
    int  (*tex_create)(domino_gfx_device*, const domino_gfx_texture_desc*, domino_gfx_texture**);
    void (*tex_destroy)(domino_gfx_texture*);
    int  (*tex_update)(domino_gfx_texture*, int, int, int, int, const void*, int);
    int  (*draw_texture)(domino_gfx_device*, domino_gfx_texture*, const domino_gfx_rect*, const domino_gfx_uv_rect*);
    int  (*draw_text)(domino_gfx_device*, domino_gfx_font*, float, float, const char*, float, float, float, float);
} domino_gfx_backend_vtable;

struct domino_gfx_device {
    domino_gfx_backend backend;
    domino_gfx_profile profile;
    domino_pixfmt      framebuffer_fmt;
    int                width;
    int                height;
    int                fullscreen;
    int                vsync;

    domino_sys_context*                 sys;
    const domino_gfx_backend_vtable*    vt;
    void*                               backend_data;
};

#endif /* DOMINO_GFX_INTERNAL_H */
