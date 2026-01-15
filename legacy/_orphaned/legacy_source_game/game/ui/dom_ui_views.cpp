/*
FILE: source/dominium/game/ui/dom_ui_views.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Snapshot-driven map/transit render helpers (derived-only).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal helpers; no stable ABI guarantee.
EXTENSION POINTS: Extend via `docs/SPEC_PLAYER_CONTINUITY.md`.
*/
#include "ui/dom_ui_views.h"

#include <cstdio>

extern "C" {
#include "domino/core/fixed.h"
}

#include "runtime/dom_body_registry.h"
#include "runtime/dom_fidelity.h"

namespace dom {

namespace {

static int dom_min_int(int a, int b) {
    return (a < b) ? a : b;
}

static int dom_max_int(int a, int b) {
    return (a > b) ? a : b;
}

static d_gfx_color dom_make_color(u8 r, u8 g, u8 b, u8 a) {
    d_gfx_color c;
    c.a = a;
    c.r = r;
    c.g = g;
    c.b = b;
    return c;
}

static d_gfx_color dom_apply_alpha(d_gfx_color c, u8 alpha) {
    u32 scaled = (u32)c.a * (u32)alpha;
    c.a = (u8)(scaled / 255u);
    return c;
}

static void dom_emit_rect(d_gfx_cmd_buffer *buf, int x, int y, int w, int h, d_gfx_color color) {
    d_gfx_draw_rect_cmd r;
    if (!buf) {
        return;
    }
    if (w <= 0 || h <= 0) {
        return;
    }
    r.x = x;
    r.y = y;
    r.w = w;
    r.h = h;
    r.color = color;
    d_gfx_cmd_draw_rect(buf, &r);
}

static void dom_emit_outline_rect(d_gfx_cmd_buffer *buf, int x, int y, int w, int h, int thickness, d_gfx_color color) {
    if (!buf) {
        return;
    }
    if (thickness < 1) {
        thickness = 1;
    }
    dom_emit_rect(buf, x, y, w, thickness, color);
    dom_emit_rect(buf, x, y + h - thickness, w, thickness, color);
    dom_emit_rect(buf, x, y, thickness, h, color);
    dom_emit_rect(buf, x + w - thickness, y, thickness, h, color);
}

static void dom_emit_text(d_gfx_cmd_buffer *buf, int x, int y, d_gfx_color color, const char *text) {
    d_gfx_draw_text_cmd t;
    if (!buf || !text) {
        return;
    }
    t.x = x;
    t.y = y;
    t.text = text;
    t.color = color;
    d_gfx_cmd_draw_text(buf, &t);
}

static void dom_emit_line_h(d_gfx_cmd_buffer *buf, int x0, int x1, int y, int thickness, d_gfx_color color) {
    if (x1 < x0) {
        int tmp = x0;
        x0 = x1;
        x1 = tmp;
    }
    dom_emit_rect(buf, x0, y - thickness / 2, x1 - x0 + 1, thickness, color);
}

static void dom_emit_line_v(d_gfx_cmd_buffer *buf, int x, int y0, int y1, int thickness, d_gfx_color color) {
    if (y1 < y0) {
        int tmp = y0;
        y0 = y1;
        y1 = tmp;
    }
    dom_emit_rect(buf, x - thickness / 2, y0, thickness, y1 - y0 + 1, color);
}

static void dom_ui_clear_if_needed(const DomUiViewParams *params, d_gfx_color color) {
    if (!params || !params->buf) {
        return;
    }
    if (params->clear) {
        d_gfx_cmd_clear(params->buf, color);
    }
}

static void dom_ui_grid_pos(int index, int count, int width, int height, int *out_x, int *out_y) {
    int cols = 4;
    int rows;
    int margin = 40;
    int usable_w;
    int usable_h;
    int col;
    int row;
    int cell_w;
    int cell_h;
    if (!out_x || !out_y) {
        return;
    }
    if (count <= 0) {
        *out_x = width / 2;
        *out_y = height / 2;
        return;
    }
    if (count > 16) cols = 6;
    if (count > 36) cols = 8;
    if (count > 72) cols = 12;
    rows = (count + cols - 1) / cols;
    if (rows < 1) rows = 1;
    usable_w = width - margin * 2;
    usable_h = height - margin * 2;
    if (usable_w < 1) usable_w = width;
    if (usable_h < 1) usable_h = height;
    cell_w = usable_w / cols;
    cell_h = usable_h / rows;
    if (cell_w < 1) cell_w = 1;
    if (cell_h < 1) cell_h = 1;
    col = index % cols;
    row = index / cols;
    *out_x = margin + col * cell_w + cell_w / 2;
    *out_y = margin + row * cell_h + cell_h / 2;
}

static int dom_ui_cosmo_include(u32 kind, int include_all) {
    if (include_all) {
        return 1;
    }
    return (kind == DOM_COSMO_KIND_GALAXY || kind == DOM_COSMO_KIND_SYSTEM) ? 1 : 0;
}

static int dom_ui_cosmo_visible_index(const dom_cosmo_map_snapshot *cosmo,
                                      u64 id,
                                      int include_all,
                                      int *out_index,
                                      int *out_count) {
    u32 i;
    int idx = 0;
    int found = 0;
    if (!cosmo) {
        return 0;
    }
    for (i = 0u; i < cosmo->entity_count; ++i) {
        const dom_cosmo_entity_view *ent = cosmo->entities + i;
        if (!dom_ui_cosmo_include(ent->kind, include_all)) {
            continue;
        }
        if (ent->id == id) {
            found = 1;
            if (out_index) {
                *out_index = idx;
            }
        }
        idx++;
    }
    if (out_count) {
        *out_count = idx;
    }
    return found;
}

static d_gfx_color dom_ui_cosmo_color(u32 kind, u8 alpha) {
    d_gfx_color c;
    switch (kind) {
    case DOM_COSMO_KIND_FILAMENT:
        c = dom_make_color(0x80u, 0x60u, 0xc0u, 0xffu);
        break;
    case DOM_COSMO_KIND_CLUSTER:
        c = dom_make_color(0x40u, 0xa0u, 0xc0u, 0xffu);
        break;
    case DOM_COSMO_KIND_GALAXY:
        c = dom_make_color(0x60u, 0x90u, 0xffu, 0xffu);
        break;
    case DOM_COSMO_KIND_SYSTEM:
        c = dom_make_color(0xffu, 0xd0u, 0x60u, 0xffu);
        break;
    default:
        c = dom_make_color(0x90u, 0x90u, 0x90u, 0xffu);
        break;
    }
    return dom_apply_alpha(c, alpha);
}

static d_gfx_color dom_ui_body_color(u32 kind, u8 alpha) {
    d_gfx_color c;
    switch (kind) {
    case DOM_BODY_KIND_STAR:
        c = dom_make_color(0xffu, 0xd0u, 0x40u, 0xffu);
        break;
    case DOM_BODY_KIND_PLANET:
        c = dom_make_color(0x40u, 0x90u, 0xffu, 0xffu);
        break;
    case DOM_BODY_KIND_MOON:
        c = dom_make_color(0xc0u, 0xc0u, 0xc0u, 0xffu);
        break;
    case DOM_BODY_KIND_STATION:
        c = dom_make_color(0x90u, 0xffu, 0x90u, 0xffu);
        break;
    default:
        c = dom_make_color(0x90u, 0x90u, 0x90u, 0xffu);
        break;
    }
    return dom_apply_alpha(c, alpha);
}

static d_gfx_color dom_ui_chunk_color(u32 state, u8 alpha) {
    d_gfx_color c;
    switch (state) {
    case DOM_SURFACE_CHUNK_STATE_REQUESTED:
        c = dom_make_color(0xf0u, 0xb0u, 0x40u, 0xffu);
        break;
    case DOM_SURFACE_CHUNK_STATE_ACTIVE:
        c = dom_make_color(0x60u, 0x90u, 0xffu, 0xffu);
        break;
    case DOM_SURFACE_CHUNK_STATE_READY:
        c = dom_make_color(0x40u, 0xd0u, 0x80u, 0xffu);
        break;
    default:
        c = dom_make_color(0x50u, 0x50u, 0x50u, 0xffu);
        break;
    }
    return dom_apply_alpha(c, alpha);
}

static void dom_ui_render_cosmo_internal(const DomUiViewParams *params,
                                         const dom_cosmo_map_snapshot *cosmo,
                                         int include_all) {
    u32 i;
    d_gfx_color bg = dom_make_color(0x0cu, 0x0fu, 0x18u, 0xffu);
    d_gfx_color text_col = dom_apply_alpha(dom_make_color(0xe0u, 0xe0u, 0xe0u, 0xffu), params->alpha);
    if (!params || !params->buf) {
        return;
    }
    dom_ui_clear_if_needed(params, bg);

    if (!cosmo || cosmo->entity_count == 0u) {
        dom_emit_text(params->buf, 16, 16, text_col, "Cosmos map (no data)");
        return;
    }

    if (params->fidelity >= DOM_FIDELITY_MED) {
        for (i = 0u; i < cosmo->edge_count; ++i) {
            const dom_cosmo_edge_view *edge = cosmo->edges + i;
            int idx0 = 0;
            int idx1 = 0;
            int count = 0;
            int x0;
            int y0;
            int x1;
            int y1;
            if (!dom_ui_cosmo_visible_index(cosmo, edge->src_id, include_all, &idx0, &count)) {
                continue;
            }
            if (!dom_ui_cosmo_visible_index(cosmo, edge->dst_id, include_all, &idx1, &count)) {
                continue;
            }
            dom_ui_grid_pos(idx0, count, params->width, params->height, &x0, &y0);
            dom_ui_grid_pos(idx1, count, params->width, params->height, &x1, &y1);
            {
                d_gfx_color line = dom_apply_alpha(dom_make_color(0x40u, 0x50u, 0x70u, 0xffu), params->alpha);
                dom_emit_line_h(params->buf, x0, x1, y0, 2, line);
                dom_emit_line_v(params->buf, x1, y0, y1, 2, line);
            }
        }
    }

    {
        int visible_count = 0;
        dom_ui_cosmo_visible_index(cosmo, 0u, include_all, 0, &visible_count);
        for (i = 0u; i < cosmo->entity_count; ++i) {
            const dom_cosmo_entity_view *ent = cosmo->entities + i;
            int idx = 0;
            int x;
            int y;
            int size = 8;
            char label[64];
            if (!dom_ui_cosmo_include(ent->kind, include_all)) {
                continue;
            }
            dom_ui_cosmo_visible_index(cosmo, ent->id, include_all, &idx, 0);
            dom_ui_grid_pos(idx, visible_count, params->width, params->height, &x, &y);
            if (ent->kind == DOM_COSMO_KIND_GALAXY) size = 10;
            if (ent->kind == DOM_COSMO_KIND_CLUSTER) size = 9;
            if (ent->kind == DOM_COSMO_KIND_FILAMENT) size = 7;
            dom_emit_rect(params->buf, x - size / 2, y - size / 2, size, size,
                          dom_ui_cosmo_color(ent->kind, params->alpha));
            if (params->fidelity >= DOM_FIDELITY_HIGH) {
                std::snprintf(label, sizeof(label), "id:%llu",
                              (unsigned long long)ent->id);
                dom_emit_text(params->buf, x + size + 4, y - size / 2, text_col, label);
            }
        }
    }
}

} // namespace

void dom_ui_render_planet_map(const DomUiViewParams *params,
                              const dom_surface_view_snapshot *surface,
                              const dom_body_list_snapshot *bodies) {
    d_gfx_color bg = dom_make_color(0x0eu, 0x12u, 0x20u, 0xffu);
    d_gfx_color outline = dom_apply_alpha(dom_make_color(0x60u, 0x90u, 0xffu, 0xffu), params ? params->alpha : 0xffu);
    d_gfx_color text_col = dom_apply_alpha(dom_make_color(0xe0u, 0xe0u, 0xe0u, 0xffu), params ? params->alpha : 0xffu);
    char text[128];
    int width;
    int height;
    int size;
    int half;
    int x0;
    int y0;

    if (!params || !params->buf) {
        return;
    }
    width = params->width;
    height = params->height;
    dom_ui_clear_if_needed(params, bg);

    size = dom_min_int(width, height) * 3 / 4;
    if (size < 80) size = dom_min_int(width, height) / 2;
    half = size / 2;
    x0 = width / 2 - half;
    y0 = height / 2 - half;

    dom_emit_outline_rect(params->buf, x0, y0, size, size, 2, outline);
    if (params->fidelity >= DOM_FIDELITY_MED) {
        dom_emit_line_h(params->buf, x0, x0 + size, height / 2, 1, outline);
        dom_emit_line_v(params->buf, width / 2, y0, y0 + size, 1, outline);
    }
    if (params->fidelity >= DOM_FIDELITY_HIGH) {
        d_gfx_color ring = dom_apply_alpha(dom_make_color(0x30u, 0x50u, 0x80u, 0xffu), params->alpha);
        dom_emit_outline_rect(params->buf, x0 - 6, y0 - 6, size + 12, size + 12, 1, ring);
    }

    if (surface && params->fidelity >= DOM_FIDELITY_MED && surface->chunk_count > 0u) {
        u32 i;
        int max_draw = (int)surface->chunk_count;
        int cell = 8;
        int gap = 2;
        int start_x = dom_max_int(16, width / 2 - (max_draw * (cell + gap)) / 2);
        int y = height - 24;
        if (max_draw > 32) {
            max_draw = 32;
        }
        for (i = 0u; i < (u32)max_draw; ++i) {
            const dom_surface_chunk_view *chunk = surface->chunks + i;
            int cx = start_x + (int)i * (cell + gap);
            dom_emit_rect(params->buf, cx, y, cell, cell,
                          dom_ui_chunk_color(chunk->state, params->alpha));
        }
    }

    if (surface) {
        i64 h_m = d_q48_16_to_int(surface->sampled_height_m);
        std::snprintf(text, sizeof(text), "Planet view body=%llu height=%lldm",
                      (unsigned long long)surface->body_id,
                      (long long)h_m);
    } else if (bodies && bodies->body_count > 0u) {
        std::snprintf(text, sizeof(text), "Planet view body=%llu", (unsigned long long)bodies->bodies[0].id);
    } else {
        std::snprintf(text, sizeof(text), "Planet view (no surface data)");
    }
    dom_emit_text(params->buf, 16, 16, text_col, text);
}

void dom_ui_render_system_map(const DomUiViewParams *params,
                              const dom_body_list_snapshot *bodies) {
    d_gfx_color bg = dom_make_color(0x0cu, 0x10u, 0x18u, 0xffu);
    d_gfx_color text_col = dom_apply_alpha(dom_make_color(0xe0u, 0xe0u, 0xe0u, 0xffu), params ? params->alpha : 0xffu);
    char text[128];
    int width;
    int height;
    u32 i;

    if (!params || !params->buf) {
        return;
    }
    width = params->width;
    height = params->height;
    dom_ui_clear_if_needed(params, bg);

    if (!bodies || bodies->body_count == 0u) {
        dom_emit_text(params->buf, 16, 16, text_col, "System view (no bodies)");
        return;
    }

    {
        int count = (int)bodies->body_count;
        int margin = 40;
        int usable_w = width - margin * 2;
        int y = height / 2;
        if (usable_w < 1) usable_w = width;
        for (i = 0u; i < bodies->body_count; ++i) {
            const dom_body_view *body = bodies->bodies + i;
            int x = margin + (int)(i + 1u) * (usable_w / (count + 1));
            int size = 6;
            if (body->kind == DOM_BODY_KIND_STAR) size = 12;
            if (body->kind == DOM_BODY_KIND_MOON) size = 5;
            dom_emit_rect(params->buf, x - size / 2, y - size / 2, size, size,
                          dom_ui_body_color(body->kind, params->alpha));
            if (params->fidelity >= DOM_FIDELITY_MED) {
                d_gfx_color line = dom_apply_alpha(dom_make_color(0x30u, 0x40u, 0x60u, 0xffu), params->alpha);
                dom_emit_line_v(params->buf, x, y - 24, y + 24, 1, line);
            }
            if (params->fidelity >= DOM_FIDELITY_HIGH) {
                std::snprintf(text, sizeof(text), "id:%llu", (unsigned long long)body->id);
                dom_emit_text(params->buf, x - 12, y + 10, text_col, text);
            }
        }
    }

    std::snprintf(text, sizeof(text), "System view bodies=%u", (unsigned)bodies->body_count);
    dom_emit_text(params->buf, 16, 16, text_col, text);
}

void dom_ui_render_galaxy_map(const DomUiViewParams *params,
                              const dom_cosmo_map_snapshot *cosmo) {
    dom_ui_render_cosmo_internal(params, cosmo, 0);
}

void dom_ui_render_cosmos_map(const DomUiViewParams *params,
                              const dom_cosmo_map_snapshot *cosmo) {
    dom_ui_render_cosmo_internal(params, cosmo, 1);
}

void dom_ui_render_transit_view(const DomUiViewParams *params,
                                const dom_cosmo_transit_snapshot *transit,
                                const dom_runtime_summary_snapshot *runtime) {
    d_gfx_color bg = dom_make_color(0x00u, 0x00u, 0x00u, 0xffu);
    d_gfx_color text_col = dom_apply_alpha(dom_make_color(0xe0u, 0xe0u, 0xe0u, 0xffu), params ? params->alpha : 0xffu);
    d_gfx_color bar_col = dom_apply_alpha(dom_make_color(0x60u, 0xb0u, 0xffu, 0xffu), params ? params->alpha : 0xffu);
    char text[128];
    int width;
    int height;
    int bar_w;
    int bar_h = 10;
    int bar_x;
    int bar_y;
    u32 progress = 0u;

    if (!params || !params->buf) {
        return;
    }
    width = params->width;
    height = params->height;
    dom_ui_clear_if_needed(params, bg);

    if (params->fidelity >= DOM_FIDELITY_MED) {
        d_gfx_color star = dom_apply_alpha(dom_make_color(0xa0u, 0xa0u, 0xc0u, 0xffu), params->alpha);
        dom_emit_rect(params->buf, width / 4, height / 3, 2, 2, star);
        dom_emit_rect(params->buf, width / 2, height / 4, 2, 2, star);
        dom_emit_rect(params->buf, (width * 3) / 4, height / 2, 2, 2, star);
        dom_emit_rect(params->buf, width / 3, (height * 2) / 3, 2, 2, star);
        dom_emit_rect(params->buf, (width * 2) / 3, (height * 3) / 4, 2, 2, star);
    }

    if (transit && transit->transit_active && runtime) {
        u64 start = transit->transit.start_tick;
        u64 end = transit->transit.end_tick;
        u64 now = runtime->tick_index;
        u64 span = (end > start) ? (end - start) : 1u;
        u64 elapsed = (now > start) ? (now - start) : 0u;
        if (elapsed > span) {
            elapsed = span;
        }
        progress = (u32)((elapsed * 100u) / span);
    }

    bar_w = width * 2 / 3;
    if (bar_w < 80) bar_w = dom_min_int(width, 200);
    bar_x = (width - bar_w) / 2;
    bar_y = height / 2 + 40;
    dom_emit_outline_rect(params->buf, bar_x, bar_y, bar_w, bar_h, 1,
                          dom_apply_alpha(dom_make_color(0x80u, 0x80u, 0x80u, 0xffu), params->alpha));
    if (progress > 0u) {
        int fill_w = (int)((progress * (u32)(bar_w - 2)) / 100u);
        dom_emit_rect(params->buf, bar_x + 1, bar_y + 1, fill_w, bar_h - 2, bar_col);
    }

    std::snprintf(text, sizeof(text), "Transit %u%%", (unsigned)progress);
    dom_emit_text(params->buf, bar_x, bar_y - 16, text_col, text);
    dom_emit_text(params->buf, 16, 16, text_col, "Transit view");
}

} // namespace dom
