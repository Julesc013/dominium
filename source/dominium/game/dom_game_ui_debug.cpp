#include "dom_game_ui_debug.h"

#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/fixed.h"
#include "env/d_env_field.h"
#include "env/d_env_volume.h"
#include "hydro/d_hydro.h"
#include "res/d_res.h"
#include "struct/d_struct.h"
#include "content/d_content.h"
#include "world/d_litho.h"
}

namespace dom {

static dui_widget *g_panel = (dui_widget *)0;
static dui_widget *g_toggle_button = (dui_widget *)0;
static dui_widget *g_overlay_hydro_button = (dui_widget *)0;
static dui_widget *g_overlay_temp_button = (dui_widget *)0;
static dui_widget *g_overlay_pressure_button = (dui_widget *)0;
static dui_widget *g_overlay_volumes_button = (dui_widget *)0;
static dui_widget *g_hash_label = (dui_widget *)0;
static dui_widget *g_chunk_label = (dui_widget *)0;
static dui_widget *g_res_label = (dui_widget *)0;
static dui_widget *g_struct_label = (dui_widget *)0;
static dui_widget *g_pack_label = (dui_widget *)0;
static dui_widget *g_content_label = (dui_widget *)0;
static dui_widget *g_det_label = (dui_widget *)0;
static dui_widget *g_probe_label = (dui_widget *)0;
static dui_widget *g_env_label = (dui_widget *)0;
static dui_widget *g_hydro_label = (dui_widget *)0;
static dui_widget *g_volume_label = (dui_widget *)0;
static dui_widget *g_litho_label = (dui_widget *)0;

static char g_buf_hash[128];
static char g_buf_chunk[128];
static char g_buf_res[128];
static char g_buf_struct[128];
static char g_buf_pack[192];
static char g_buf_content[192];
static char g_buf_det[96];
static char g_buf_probe[160];
static char g_buf_env[256];
static char g_buf_hydro[192];
static char g_buf_volume[256];
static char g_buf_litho[256];
static char g_buf_overlay_hydro[64];
static char g_buf_overlay_temp[64];
static char g_buf_overlay_pressure[64];
static char g_buf_overlay_volumes[64];

void dom_game_ui_debug_reset(void) {
    g_panel = (dui_widget *)0;
    g_toggle_button = (dui_widget *)0;
    g_overlay_hydro_button = (dui_widget *)0;
    g_overlay_temp_button = (dui_widget *)0;
    g_overlay_pressure_button = (dui_widget *)0;
    g_overlay_volumes_button = (dui_widget *)0;
    g_hash_label = (dui_widget *)0;
    g_chunk_label = (dui_widget *)0;
    g_res_label = (dui_widget *)0;
    g_struct_label = (dui_widget *)0;
    g_pack_label = (dui_widget *)0;
    g_content_label = (dui_widget *)0;
    g_det_label = (dui_widget *)0;
    g_probe_label = (dui_widget *)0;
    g_env_label = (dui_widget *)0;
    g_hydro_label = (dui_widget *)0;
    g_volume_label = (dui_widget *)0;
    g_litho_label = (dui_widget *)0;
}

static void on_toggle_debug(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->toggle_debug_panel();
    }
}

static void on_toggle_overlay_hydro(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->toggle_overlay_hydrology();
    }
}

static void on_toggle_overlay_temp(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->toggle_overlay_temperature();
    }
}

static void on_toggle_overlay_pressure(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->toggle_overlay_pressure();
    }
}

static void on_toggle_overlay_volumes(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    if (app) {
        app->toggle_overlay_volumes();
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
        g_panel->layout_rect.h = d_q16_16_from_int(420);
        dui_widget_add_child(ctx.root, g_panel);

        g_hash_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_chunk_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_res_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_struct_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_pack_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_content_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_det_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_probe_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_env_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_hydro_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_volume_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_litho_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);

        g_overlay_hydro_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        g_overlay_temp_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        g_overlay_pressure_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        g_overlay_volumes_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);

        if (g_hash_label) dui_widget_add_child(g_panel, g_hash_label);
        if (g_chunk_label) dui_widget_add_child(g_panel, g_chunk_label);
        if (g_res_label) dui_widget_add_child(g_panel, g_res_label);
        if (g_struct_label) dui_widget_add_child(g_panel, g_struct_label);
        if (g_pack_label) dui_widget_add_child(g_panel, g_pack_label);
        if (g_content_label) dui_widget_add_child(g_panel, g_content_label);
        if (g_det_label) dui_widget_add_child(g_panel, g_det_label);
        if (g_probe_label) dui_widget_add_child(g_panel, g_probe_label);
        if (g_env_label) dui_widget_add_child(g_panel, g_env_label);
        if (g_hydro_label) dui_widget_add_child(g_panel, g_hydro_label);
        if (g_volume_label) dui_widget_add_child(g_panel, g_volume_label);
        if (g_litho_label) dui_widget_add_child(g_panel, g_litho_label);

        if (g_overlay_hydro_button) {
            g_overlay_hydro_button->on_click = on_toggle_overlay_hydro;
            g_overlay_hydro_button->user_data = (void *)&app;
            dui_widget_add_child(g_panel, g_overlay_hydro_button);
        }
        if (g_overlay_temp_button) {
            g_overlay_temp_button->on_click = on_toggle_overlay_temp;
            g_overlay_temp_button->user_data = (void *)&app;
            dui_widget_add_child(g_panel, g_overlay_temp_button);
        }
        if (g_overlay_pressure_button) {
            g_overlay_pressure_button->on_click = on_toggle_overlay_pressure;
            g_overlay_pressure_button->user_data = (void *)&app;
            dui_widget_add_child(g_panel, g_overlay_pressure_button);
        }
        if (g_overlay_volumes_button) {
            g_overlay_volumes_button->on_click = on_toggle_overlay_volumes;
            g_overlay_volumes_button->user_data = (void *)&app;
            dui_widget_add_child(g_panel, g_overlay_volumes_button);
        }
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

static q16_16 find_env_field0(const d_env_sample *samples, u16 count, d_env_field_id field_id) {
    u16 i;
    if (!samples || count == 0u) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (samples[i].field_id == field_id) {
            return samples[i].values[0];
        }
    }
    return 0;
}

static void update_probe_samples(DomGameApp &app, d_world *w) {
    q32_32 px;
    q32_32 py;
    q32_32 pz;

    d_env_sample env_samples[16];
    u16 env_count;

    d_hydro_cell hydro_cell;
    int hydro_ok;

    d_env_volume_id vol_id;
    const d_env_volume *vol;

    d_world_layers layers;
    int litho_ok;

    if (!w) {
        return;
    }

    app.debug_probe_world_coords(&px, &py, &pz);

    std::snprintf(g_buf_probe, sizeof(g_buf_probe),
                  "Probe: cx=%d cy=%d%s",
                  (int)(px >> Q32_32_FRAC_BITS),
                  (int)(py >> Q32_32_FRAC_BITS),
                  app.debug_probe_is_set() ? " (pinned)" : " (camera)");
    if (g_probe_label) {
        g_probe_label->text = g_buf_probe;
    }

    env_count = d_env_sample_at(w, px, py, pz, env_samples, 16u);
    {
        q16_16 p = find_env_field0(env_samples, env_count, D_ENV_FIELD_PRESSURE);
        q16_16 t = find_env_field0(env_samples, env_count, D_ENV_FIELD_TEMPERATURE);
        q16_16 g0 = find_env_field0(env_samples, env_count, D_ENV_FIELD_GAS0_FRACTION);
        q16_16 g1 = find_env_field0(env_samples, env_count, D_ENV_FIELD_GAS1_FRACTION);
        q16_16 h = find_env_field0(env_samples, env_count, D_ENV_FIELD_HUMIDITY);
        q16_16 wx = find_env_field0(env_samples, env_count, D_ENV_FIELD_WIND_X);
        q16_16 wy = find_env_field0(env_samples, env_count, D_ENV_FIELD_WIND_Y);
        std::snprintf(g_buf_env, sizeof(g_buf_env),
                      "ENV: P=%d T=%d G0=%.1f%% G1=%.3f%% H=%.1f%% Wx=%d Wy=%d (n=%u)",
                      d_q16_16_to_int(p),
                      d_q16_16_to_int(t),
                      d_q16_16_to_double(g0) * 100.0,
                      d_q16_16_to_double(g1) * 100.0,
                      d_q16_16_to_double(h) * 100.0,
                      d_q16_16_to_int(wx),
                      d_q16_16_to_int(wy),
                      (unsigned)env_count);
    }
    if (g_env_label) {
        g_env_label->text = g_buf_env;
    }

    std::memset(&hydro_cell, 0, sizeof(hydro_cell));
    hydro_ok = (d_hydro_sample_at(w, px, py, pz, &hydro_cell) == 0) ? 1 : 0;
    if (hydro_ok) {
        std::snprintf(g_buf_hydro, sizeof(g_buf_hydro),
                      "Hydro: depth=%d surf=%d vx=%d vy=%d",
                      d_q16_16_to_int(hydro_cell.depth),
                      d_q16_16_to_int(hydro_cell.surface_height),
                      d_q16_16_to_int(hydro_cell.velocity_x),
                      d_q16_16_to_int(hydro_cell.velocity_y));
    } else {
        std::snprintf(g_buf_hydro, sizeof(g_buf_hydro),
                      "Hydro: (n/a)");
    }
    if (g_hydro_label) {
        g_hydro_label->text = g_buf_hydro;
    }

    vol_id = d_env_volume_find_at(w, px, py, pz);
    vol = (vol_id != 0u) ? d_env_volume_get(w, vol_id) : (const d_env_volume *)0;
    if (vol) {
        std::snprintf(g_buf_volume, sizeof(g_buf_volume),
                      "Volume #%u: P=%d T=%d G0=%.1f%% H=%.1f%%",
                      (unsigned)vol->id,
                      d_q16_16_to_int(vol->pressure),
                      d_q16_16_to_int(vol->temperature),
                      d_q16_16_to_double(vol->gas0_fraction) * 100.0,
                      d_q16_16_to_double(vol->humidity) * 100.0);
    } else {
        std::snprintf(g_buf_volume, sizeof(g_buf_volume),
                      "Volume: exterior");
    }
    if (g_volume_label) {
        g_volume_label->text = g_buf_volume;
    }

    std::memset(&layers, 0, sizeof(layers));
    litho_ok = (d_litho_layers_at(w, px, py, &layers) == 0) ? 1 : 0;
    if (litho_ok) {
        size_t pos = 0u;
        int written;
        u16 i;
        written = std::snprintf(g_buf_litho, sizeof(g_buf_litho),
                                "Litho: layers=%u", (unsigned)layers.layer_count);
        if (written > 0) {
            pos = (size_t)written;
        }
        for (i = 0u; i < layers.layer_count && i < 3u && pos + 16u < sizeof(g_buf_litho); ++i) {
            written = std::snprintf(g_buf_litho + pos, sizeof(g_buf_litho) - pos,
                                    " m%u:%d",
                                    (unsigned)layers.layers[i].material_id,
                                    d_q16_16_to_int(layers.layers[i].thickness));
            if (written > 0) {
                pos += (size_t)written;
            }
        }
    } else {
        std::snprintf(g_buf_litho, sizeof(g_buf_litho),
                      "Litho: (n/a)");
    }
    if (g_litho_label) {
        g_litho_label->text = g_buf_litho;
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

    std::snprintf(g_buf_overlay_hydro, sizeof(g_buf_overlay_hydro),
                  "Overlay Hydrology: %s", app.overlay_hydrology() ? "ON" : "OFF");
    if (g_overlay_hydro_button) g_overlay_hydro_button->text = g_buf_overlay_hydro;

    std::snprintf(g_buf_overlay_temp, sizeof(g_buf_overlay_temp),
                  "Overlay Temperature: %s", app.overlay_temperature() ? "ON" : "OFF");
    if (g_overlay_temp_button) g_overlay_temp_button->text = g_buf_overlay_temp;

    std::snprintf(g_buf_overlay_pressure, sizeof(g_buf_overlay_pressure),
                  "Overlay Pressure: %s", app.overlay_pressure() ? "ON" : "OFF");
    if (g_overlay_pressure_button) g_overlay_pressure_button->text = g_buf_overlay_pressure;

    std::snprintf(g_buf_overlay_volumes, sizeof(g_buf_overlay_volumes),
                  "Overlay Volumes: %s", app.overlay_volumes() ? "ON" : "OFF");
    if (g_overlay_volumes_button) g_overlay_volumes_button->text = g_buf_overlay_volumes;

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
    update_probe_samples(app, w);

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
