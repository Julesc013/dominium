#include "dom_game_ui_debug.h"

#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/fixed.h"
#include "res/d_res.h"
#include "struct/d_struct.h"
#include "content/d_content.h"
}

namespace dom {

static dui_widget *g_panel = (dui_widget *)0;
static dui_widget *g_toggle_button = (dui_widget *)0;
static dui_widget *g_hash_label = (dui_widget *)0;
static dui_widget *g_chunk_label = (dui_widget *)0;
static dui_widget *g_res_label = (dui_widget *)0;
static dui_widget *g_struct_label = (dui_widget *)0;
static dui_widget *g_pack_label = (dui_widget *)0;
static dui_widget *g_content_label = (dui_widget *)0;
static dui_widget *g_det_label = (dui_widget *)0;

static char g_buf_hash[128];
static char g_buf_chunk[128];
static char g_buf_res[128];
static char g_buf_struct[128];
static char g_buf_pack[192];
static char g_buf_content[192];
static char g_buf_det[96];

void dom_game_ui_debug_reset(void) {
    g_panel = (dui_widget *)0;
    g_toggle_button = (dui_widget *)0;
    g_hash_label = (dui_widget *)0;
    g_chunk_label = (dui_widget *)0;
    g_res_label = (dui_widget *)0;
    g_struct_label = (dui_widget *)0;
    g_pack_label = (dui_widget *)0;
    g_content_label = (dui_widget *)0;
    g_det_label = (dui_widget *)0;
}

static void on_toggle_debug(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->toggle_debug_panel();
    }
}

static void ensure_widgets(dui_context &ctx, DomGameApp &app) {
    if (!ctx.root) {
        return;
    }
    if (!g_toggle_button) {
        g_toggle_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        if (g_toggle_button) {
            g_toggle_button->text = "Toggle Debug Panel";
            g_toggle_button->on_click = on_toggle_debug;
            g_toggle_button->user_data = (void *)&app;
            dui_widget_add_child(ctx.root, g_toggle_button);
        }
    }
    if (!g_panel) {
        g_panel = dui_widget_create(&ctx, DUI_WIDGET_PANEL);
        if (!g_panel) {
            return;
        }
        g_panel->layout_rect.y = d_q16_16_from_int(64);
        dui_widget_add_child(ctx.root, g_panel);

        g_hash_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_chunk_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_res_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_struct_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_pack_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_content_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_det_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);

        if (g_hash_label) dui_widget_add_child(g_panel, g_hash_label);
        if (g_chunk_label) dui_widget_add_child(g_panel, g_chunk_label);
        if (g_res_label) dui_widget_add_child(g_panel, g_res_label);
        if (g_struct_label) dui_widget_add_child(g_panel, g_struct_label);
        if (g_pack_label) dui_widget_add_child(g_panel, g_pack_label);
        if (g_content_label) dui_widget_add_child(g_panel, g_content_label);
        if (g_det_label) dui_widget_add_child(g_panel, g_det_label);
    }
}

static void update_resource_sample(DomGameApp &app, d_world *w) {
    dres_sample sample;
    u16 count = 1u;
    GameCamera cam = app.camera();
    q32_32 sx = ((q32_32)d_q16_16_from_double((double)cam.cx)) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
    q32_32 sy = ((q32_32)d_q16_16_from_double((double)cam.cy)) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
    q32_32 sz = 0;

    g_buf_res[0] = '\0';
    if (dres_sample_at(w, sx, sy, sz, 0u, &sample, &count) == 0 && count > 0u) {
        std::snprintf(g_buf_res, sizeof(g_buf_res),
                      "Resource sample: channel=%u value0=%d",
                      (unsigned)sample.channel_id,
                      d_q16_16_to_int(sample.value[0]));
    } else {
        std::snprintf(g_buf_res, sizeof(g_buf_res),
                      "Resource sample: (none)");
    }
    if (g_res_label) {
        g_res_label->text = g_buf_res;
    }
}

static void update_pack_info(const InstanceInfo &inst) {
    size_t i;
    size_t pos = 0u;
    int written;
    g_buf_pack[0] = '\0';
    written = std::snprintf(g_buf_pack, sizeof(g_buf_pack), "Packs:");
    if (written > 0) pos = (size_t)written;
    for (i = 0u; i < inst.packs.size() && pos + 8 < sizeof(g_buf_pack); ++i) {
        written = std::snprintf(g_buf_pack + pos, sizeof(g_buf_pack) - pos,
                                " %s(%u)", inst.packs[i].id.c_str(),
                                (unsigned)inst.packs[i].version);
        if (written > 0) pos += (size_t)written;
    }
    written = std::snprintf(g_buf_pack + pos, sizeof(g_buf_pack) - pos, " Mods:");
    if (written > 0) pos += (size_t)written;
    for (i = 0u; i < inst.mods.size() && pos + 8 < sizeof(g_buf_pack); ++i) {
        written = std::snprintf(g_buf_pack + pos, sizeof(g_buf_pack) - pos,
                                " %s(%u)", inst.mods[i].id.c_str(),
                                (unsigned)inst.mods[i].version);
        if (written > 0) pos += (size_t)written;
    }
    if (g_pack_label) {
        g_pack_label->text = g_buf_pack;
    }
}

static const char *determinism_text(u32 mode) {
    switch (mode) {
    case 1u: return "Record";
    case 2u: return "Playback";
    case 3u: return "Assert";
    default: return "Off";
    }
}

void dom_game_ui_debug_update(dui_context &ctx, DomGameApp &app, d_world_hash hash) {
    d_world *w = app.session().world();
    const InstanceInfo &inst = app.session().instance();
    ensure_widgets(ctx, app);

    if (g_panel) {
        if (app.debug_panel_visible()) {
            g_panel->flags |= DUI_WIDGET_VISIBLE;
        } else {
            g_panel->flags &= ~DUI_WIDGET_VISIBLE;
        }
    }
    if (!app.debug_panel_visible() || !w) {
        return;
    }

    std::snprintf(g_buf_hash, sizeof(g_buf_hash),
                  "World hash: 0x%016llx", (unsigned long long)hash);
    if (g_hash_label) g_hash_label->text = g_buf_hash;

    if (w->chunk_count > 0u && w->chunks) {
        std::snprintf(g_buf_chunk, sizeof(g_buf_chunk),
                      "Chunks: %u (first: %d,%d)",
                      (unsigned)w->chunk_count,
                      (int)w->chunks[0].cx, (int)w->chunks[0].cy);
    } else {
        std::snprintf(g_buf_chunk, sizeof(g_buf_chunk),
                      "Chunks: 0");
    }
    if (g_chunk_label) g_chunk_label->text = g_buf_chunk;

    update_resource_sample(app, w);

    std::snprintf(g_buf_struct, sizeof(g_buf_struct),
                  "Structures: %u", (unsigned)d_struct_count(w));
    if (g_struct_label) g_struct_label->text = g_buf_struct;

    std::snprintf(g_buf_content, sizeof(g_buf_content),
                  "Content: mat=%u item=%u struct=%u proc=%u",
                  (unsigned)d_content_material_count(),
                  (unsigned)d_content_item_count(),
                  (unsigned)d_content_structure_count(),
                  (unsigned)d_content_process_count());
    if (g_content_label) g_content_label->text = g_buf_content;

    std::snprintf(g_buf_det, sizeof(g_buf_det),
                  "Determinism: %s", determinism_text(app.determinism_mode()));
    if (g_det_label) g_det_label->text = g_buf_det;

    update_pack_info(inst);
}

} // namespace dom
