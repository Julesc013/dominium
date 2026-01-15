/*
FILE: source/domino/render/pipeline.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/pipeline
RESPONSIBILITY: Implements `pipeline`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/render/pipeline.h"

#include <stdlib.h>
#include <string.h>
#include "domino/gfx.h"
#include "soft/soft_raster.h"
#include "soft/soft_config.h"

typedef struct d_gfx_soft_state {
    soft_framebuffer  fb;
    dgfx_soft_config  config;
    dgfx_viewport_t   viewport;
    int               has_framebuffer;
} d_gfx_soft_state;

struct d_gfx_pipeline {
    d_gfx_backend_type backend;
};

struct d_gfx_target {
    d_gfx_pipeline* pipe;
    int             width;
    int             height;
    d_gfx_soft_state soft;
};

struct d_gfx_pass {
    d_gfx_pipeline* pipe;
    d_gfx_target*   target;
    int             in_frame;
};

static void d_gfx_soft_reset_state(d_gfx_soft_state* st) {
    if (!st) {
        return;
    }
    st->viewport.x = 0;
    st->viewport.y = 0;
    st->viewport.w = st->has_framebuffer ? st->fb.width : 0;
    st->viewport.h = st->has_framebuffer ? st->fb.height : 0;
}

static int d_gfx_soft_init_target(d_gfx_target* tgt, i32 width, i32 height) {
    if (!tgt) {
        return 0;
    }
    memset(&tgt->soft, 0, sizeof(tgt->soft));
    dgfx_soft_config_get_default(&tgt->soft.config);
    dgfx_soft_config_apply_profile(&tgt->soft.config, tgt->soft.config.profile);
    tgt->soft.has_framebuffer = soft_fb_create(&tgt->soft.fb,
                                               width,
                                               height,
                                               tgt->soft.config.color_format,
                                               tgt->soft.config.depth_bits,
                                               tgt->soft.config.stencil_bits) ? 1 : 0;
    tgt->width = width;
    tgt->height = height;
    if (!tgt->soft.has_framebuffer) {
        return 0;
    }
    d_gfx_soft_reset_state(&tgt->soft);
    return 1;
}

static void d_gfx_soft_destroy_target(d_gfx_target* tgt) {
    if (!tgt) {
        return;
    }
    if (tgt->soft.has_framebuffer) {
        soft_fb_destroy(&tgt->soft.fb);
    }
    memset(&tgt->soft, 0, sizeof(tgt->soft));
    tgt->width = 0;
    tgt->height = 0;
}

static void d_gfx_soft_clear(d_gfx_target* tgt, uint32_t rgba) {
    if (!tgt || !tgt->soft.has_framebuffer) {
        return;
    }
    soft_raster_clear_color(&tgt->soft.fb,
                            (uint8_t)((rgba >> 16) & 0xffu),
                            (uint8_t)((rgba >> 8) & 0xffu),
                            (uint8_t)(rgba & 0xffu),
                            (uint8_t)((rgba >> 24) & 0xffu));
    if (tgt->soft.config.features.enable_depth) {
        soft_raster_clear_depth(&tgt->soft.fb, 1.0f);
    }
    if (tgt->soft.config.features.enable_stencil) {
        soft_raster_clear_stencil(&tgt->soft.fb, 0u);
    }
}

static void d_gfx_soft_draw_sprites(d_gfx_target* tgt, const d_gfx_ir_command* cmd) {
    const dgfx_sprite_t* sprites;
    uint32_t count;
    uint32_t i;

    if (!tgt || !tgt->soft.has_framebuffer || !cmd || !cmd->payload) {
        return;
    }
    if (cmd->payload_size < sizeof(dgfx_sprite_t)) {
        return;
    }
    count = cmd->payload_size / (uint32_t)sizeof(dgfx_sprite_t);
    sprites = (const dgfx_sprite_t*)cmd->payload;
    for (i = 0u; i < count; ++i) {
        const dgfx_sprite_t* spr;
        int x0;
        int y0;
        int x1;
        int y1;
        int w;
        int h;

        spr = sprites + i;
        x0 = spr->x + tgt->soft.viewport.x;
        y0 = spr->y + tgt->soft.viewport.y;
        x1 = x0 + spr->w;
        y1 = y0 + spr->h;

        if (x0 < tgt->soft.viewport.x) x0 = tgt->soft.viewport.x;
        if (y0 < tgt->soft.viewport.y) y0 = tgt->soft.viewport.y;
        if (x1 > tgt->soft.viewport.x + tgt->soft.viewport.w) x1 = tgt->soft.viewport.x + tgt->soft.viewport.w;
        if (y1 > tgt->soft.viewport.y + tgt->soft.viewport.h) y1 = tgt->soft.viewport.y + tgt->soft.viewport.h;

        w = x1 - x0;
        h = y1 - y0;
        if (w > 0 && h > 0) {
            soft_raster_fill_rect_2d(&tgt->soft.fb, x0, y0, w, h, spr->color_rgba);
        }
    }
}

static void d_gfx_soft_draw_lines(d_gfx_target* tgt, const d_gfx_ir_command* cmd) {
    const dgfx_line_segment_t* lines;
    uint32_t count;
    uint32_t i;
    if (!tgt || !tgt->soft.has_framebuffer || !cmd || !cmd->payload) {
        return;
    }
    if (cmd->payload_size < sizeof(dgfx_line_segment_t)) {
        return;
    }
    count = cmd->payload_size / (uint32_t)sizeof(dgfx_line_segment_t);
    lines = (const dgfx_line_segment_t*)cmd->payload;
    for (i = 0u; i < count; ++i) {
        const dgfx_line_segment_t* ln = lines + i;
        int x0 = ln->x0 + tgt->soft.viewport.x;
        int y0 = ln->y0 + tgt->soft.viewport.y;
        int x1 = ln->x1 + tgt->soft.viewport.x;
        int y1 = ln->y1 + tgt->soft.viewport.y;
        soft_raster_draw_line_2d(&tgt->soft.fb, x0, y0, x1, y1, ln->color_rgba);
    }
}

static void d_gfx_soft_draw_meshes(d_gfx_target* tgt, const d_gfx_ir_command* cmd) {
    const dgfx_mesh_draw_t* meshes;
    uint32_t count;
    uint32_t i;
    if (!tgt || !tgt->soft.has_framebuffer || !cmd || !cmd->payload) {
        return;
    }
    if (cmd->payload_size < sizeof(dgfx_mesh_draw_t)) {
        return;
    }
    count = cmd->payload_size / (uint32_t)sizeof(dgfx_mesh_draw_t);
    meshes = (const dgfx_mesh_draw_t*)cmd->payload;
    for (i = 0u; i < count; ++i) {
        const dgfx_mesh_draw_t* m = meshes + i;
        uint32_t tri;
        if (!m->positions || !m->indices || m->index_count < 3u) {
            continue;
        }
        for (tri = 0u; tri + 2u < m->index_count; tri += 3u) {
            uint32_t i0 = m->indices[tri + 0u];
            uint32_t i1 = m->indices[tri + 1u];
            uint32_t i2 = m->indices[tri + 2u];
            soft_vertex v0;
            soft_vertex v1;
            soft_vertex v2;
            const float* p0;
            const float* p1;
            const float* p2;

            if (i0 >= m->vertex_count || i1 >= m->vertex_count || i2 >= m->vertex_count) {
                continue;
            }
            p0 = m->positions + ((size_t)i0 * 3u);
            p1 = m->positions + ((size_t)i1 * 3u);
            p2 = m->positions + ((size_t)i2 * 3u);

            v0.x = p0[0] + (float)tgt->soft.viewport.x; v0.y = p0[1] + (float)tgt->soft.viewport.y;
            v1.x = p1[0] + (float)tgt->soft.viewport.x; v1.y = p1[1] + (float)tgt->soft.viewport.y;
            v2.x = p2[0] + (float)tgt->soft.viewport.x; v2.y = p2[1] + (float)tgt->soft.viewport.y;
            v0.z = p0[2]; v1.z = p1[2]; v2.z = p2[2];
            v0.w = v1.w = v2.w = 1.0f;
            v0.u = v1.u = v2.u = 0.0f;
            v0.v = v1.v = v2.v = 0.0f;
            v0.rgba = v1.rgba = v2.rgba = 0xffffffffu;
            soft_raster_draw_triangle(&tgt->soft.fb, &v0, &v1, &v2,
                                      tgt->soft.config.features.enable_depth ? 1 : 0);
        }
    }
}

static void d_gfx_soft_draw_text(d_gfx_target* tgt, const d_gfx_ir_command* cmd) {
    if (!tgt || !tgt->soft.has_framebuffer || !cmd || !cmd->payload) {
        return;
    }
    if (cmd->payload_size < sizeof(dgfx_text_draw_t)) {
        return;
    }
    {
        const dgfx_text_draw_t* t = (const dgfx_text_draw_t*)cmd->payload;
        int x = t->x + tgt->soft.viewport.x;
        int y = t->y + tgt->soft.viewport.y;
        if (!t->utf8_text) {
            return;
        }
        soft_raster_draw_text_stub(&tgt->soft.fb, x, y, t->color_rgba, t->utf8_text);
    }
}

static void d_gfx_soft_dispatch(d_gfx_target* tgt, const d_gfx_ir_command* cmd) {
    switch (cmd->opcode) {
    case DGFX_CMD_CLEAR:
        if (cmd->payload && cmd->payload_size >= sizeof(uint32_t)) {
            uint32_t rgba;
            memcpy(&rgba, cmd->payload, sizeof(uint32_t));
            d_gfx_soft_clear(tgt, rgba);
        } else {
            d_gfx_soft_clear(tgt, 0xff000000u);
        }
        break;
    case DGFX_CMD_SET_VIEWPORT:
        if (cmd->payload && cmd->payload_size >= sizeof(dgfx_viewport_t)) {
            memcpy(&tgt->soft.viewport, cmd->payload, sizeof(dgfx_viewport_t));
        }
        break;
    case DGFX_CMD_SET_CAMERA:
        /* Camera state is currently unused in the software interpreter. */
        break;
    case DGFX_CMD_DRAW_SPRITES:
        d_gfx_soft_draw_sprites(tgt, cmd);
        break;
    case DGFX_CMD_DRAW_LINES:
        d_gfx_soft_draw_lines(tgt, cmd);
        break;
    case DGFX_CMD_DRAW_MESHES:
        d_gfx_soft_draw_meshes(tgt, cmd);
        break;
    case DGFX_CMD_DRAW_TEXT:
        d_gfx_soft_draw_text(tgt, cmd);
        break;
    default:
        /* Unsupported opcodes are ignored. */
        break;
    }
}

d_gfx_material d_gfx_material_default(void) {
    d_gfx_material m;
    m.id = 0u;
    return m;
}

d_gfx_pipeline* d_gfx_pipeline_create(d_gfx_backend_type backend) {
    d_gfx_pipeline* pipe;
    if (backend != D_GFX_BACKEND_SOFT) {
        return NULL;
    }
    pipe = (d_gfx_pipeline*)malloc(sizeof(d_gfx_pipeline));
    if (!pipe) {
        return NULL;
    }
    pipe->backend = backend;
    return pipe;
}

void d_gfx_pipeline_destroy(d_gfx_pipeline* pipe) {
    if (!pipe) {
        return;
    }
    free(pipe);
}

d_gfx_target* d_gfx_target_create(d_gfx_pipeline* pipe, i32 width, i32 height) {
    d_gfx_target* tgt;
    if (!pipe || width <= 0 || height <= 0) {
        return NULL;
    }
    if (pipe->backend != D_GFX_BACKEND_SOFT) {
        return NULL;
    }
    tgt = (d_gfx_target*)malloc(sizeof(d_gfx_target));
    if (!tgt) {
        return NULL;
    }
    memset(tgt, 0, sizeof(*tgt));
    tgt->pipe = pipe;
    if (!d_gfx_soft_init_target(tgt, width, height)) {
        free(tgt);
        return NULL;
    }
    return tgt;
}

void d_gfx_target_destroy(d_gfx_pipeline* pipe, d_gfx_target* target) {
    (void)pipe;
    if (!target) {
        return;
    }
    d_gfx_soft_destroy_target(target);
    free(target);
}

d_gfx_pass* d_gfx_pass_create(d_gfx_pipeline* pipe, d_gfx_target* target) {
    d_gfx_pass* pass;
    if (!pipe || !target) {
        return NULL;
    }
    if (pipe->backend != D_GFX_BACKEND_SOFT) {
        return NULL;
    }
    pass = (d_gfx_pass*)malloc(sizeof(d_gfx_pass));
    if (!pass) {
        return NULL;
    }
    memset(pass, 0, sizeof(*pass));
    pass->pipe = pipe;
    pass->target = target;
    return pass;
}

void d_gfx_pass_destroy(d_gfx_pipeline* pipe, d_gfx_pass* pass) {
    (void)pipe;
    if (!pass) {
        return;
    }
    free(pass);
}

void d_gfx_pass_begin(d_gfx_pass* pass) {
    if (!pass || !pass->target) {
        return;
    }
    pass->in_frame = 1;
    d_gfx_soft_clear(pass->target, 0xff000000u);
}

void d_gfx_pass_end(d_gfx_pass* pass) {
    if (!pass) {
        return;
    }
    pass->in_frame = 0;
}

void d_gfx_pass_submit_ir(d_gfx_pass* pass, const struct d_gfx_ir_command* cmds, u32 count) {
    u32 i;
    if (!pass || !pass->target || !cmds) {
        return;
    }
    if (!pass->in_frame) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        d_gfx_soft_dispatch(pass->target, cmds + i);
    }
}
