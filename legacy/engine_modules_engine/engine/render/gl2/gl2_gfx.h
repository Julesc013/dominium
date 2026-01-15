/*
FILE: source/domino/render/gl2/gl2_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/gl2/gl2_gfx
RESPONSIBILITY: Defines internal contract for `gl2_gfx`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_GL2_GFX_H
#define DOMINIUM_GL2_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* gl2 renderer state */
typedef struct gl2_state_t {
    dsys_window* window;       /* dsys window pointer */
    void*        native_window;/* platform-specific native handle */

    int          width;
    int          height;
    int          fullscreen;
    int          vsync;

    int          platform;     /* 1=Win32, 2=Cocoa, 3=X11 */

    void*        gl_context;   /* HGLRC / GLXContext / NSOpenGLContext */
    void*        gl_drawable;  /* HDC / Window / view */

    dgfx_caps    caps;

    int          frame_in_progress;

    /* Core GL objects */
    unsigned int program_2d;
    unsigned int program_3d;
    unsigned int program_lines;

    unsigned int vbo_sprites;
    unsigned int vbo_lines;
    unsigned int vbo_mesh;
    unsigned int ibo_mesh;

    /* Uniform locations */
    int          u_2d_mvp;
    int          u_2d_color;
    int          u_2d_tex;

    int          u_3d_view;
    int          u_3d_proj;
    int          u_3d_world;

    int          u_lines_mvp;
    int          u_lines_color;

    /* Attribute locations */
    int          a_2d_pos;
    int          a_2d_color;
    int          a_2d_uv;

    int          a_lines_pos;
    int          a_lines_color;

    /* Cached matrices */
    float        view[16];
    float        proj[16];
    float        world[16];

    int          current_pipeline;
} gl2_state_t;

extern gl2_state_t g_gl2;

const dgfx_backend_vtable* dgfx_gl2_get_vtable(void);

#endif /* DOMINIUM_GL2_GFX_H */
