/*
FILE: source/dominium/game/dom_game_ui_debug.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_ui_debug
RESPONSIBILITY: Implements `dom_game_ui_debug`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_game_ui_debug.h"

#include <cstdio>
#include <cstdarg>
#include <cstring>

extern "C" {
#include "domino/core/fixed.h"
#include "env/d_env_field.h"
#include "env/d_env_volume.h"
#include "hydro/d_hydro.h"
#include "net/d_net_schema.h"
#include "res/d_res.h"
#include "core/d_account.h"
#include "core/d_org.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"
#include "econ/d_econ_metrics.h"
#include "policy/d_policy.h"
#include "research/d_research_state.h"
#include "ai/d_agent.h"
#include "job/d_job.h"
#include "struct/d_struct.h"
#include "content/d_content.h"
#include "sim/d_sim_process.h"
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
static dui_widget *g_net_label = (dui_widget *)0;
static dui_widget *g_probe_label = (dui_widget *)0;
static dui_widget *g_env_label = (dui_widget *)0;
static dui_widget *g_hydro_label = (dui_widget *)0;
static dui_widget *g_volume_label = (dui_widget *)0;
static dui_widget *g_litho_label = (dui_widget *)0;
static dui_widget *g_machine_label = (dui_widget *)0;
static dui_widget *g_jobs_label = (dui_widget *)0;
static dui_widget *g_agents_label = (dui_widget *)0;
static dui_widget *g_throughput_label = (dui_widget *)0;
static dui_widget *g_org_label = (dui_widget *)0;
static dui_widget *g_econ_label = (dui_widget *)0;
static dui_widget *g_research_label = (dui_widget *)0;
static dui_widget *g_research_next_button = (dui_widget *)0;

static char g_buf_hash[128];
static char g_buf_chunk[128];
static char g_buf_res[128];
static char g_buf_struct[128];
static char g_buf_pack[192];
static char g_buf_content[192];
static char g_buf_det[96];
static char g_buf_net[768];
static char g_buf_probe[160];
static char g_buf_env[256];
static char g_buf_hydro[192];
static char g_buf_volume[256];
static char g_buf_litho[256];
static char g_buf_machines[512];
static char g_buf_jobs[512];
static char g_buf_agents[512];
static char g_buf_throughput[512];
static char g_buf_org[512];
static char g_buf_econ[512];
static char g_buf_research[768];
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
    g_net_label = (dui_widget *)0;
    g_probe_label = (dui_widget *)0;
    g_env_label = (dui_widget *)0;
    g_hydro_label = (dui_widget *)0;
    g_volume_label = (dui_widget *)0;
    g_litho_label = (dui_widget *)0;
    g_machine_label = (dui_widget *)0;
    g_jobs_label = (dui_widget *)0;
    g_agents_label = (dui_widget *)0;
    g_throughput_label = (dui_widget *)0;
    g_org_label = (dui_widget *)0;
    g_econ_label = (dui_widget *)0;
    g_research_label = (dui_widget *)0;
    g_research_next_button = (dui_widget *)0;
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

static void on_research_set_next(dui_widget *self) {
    DomGameApp *app = self ? (DomGameApp *)self->user_data : (DomGameApp *)0;
    d_org_id org_id;
    d_research_org_state st;
    d_research_id active = 0u;
    d_research_id best_above = 0u;
    d_research_id best_any = 0u;
    u32 i;
    d_research_id target = 0u;

    if (!app) {
        return;
    }
    org_id = app->player_org_id();
    if (org_id == 0u) {
        return;
    }
    if (d_research_get_org_state(org_id, &st) != 0 || st.research_count == 0u || !st.researches) {
        return;
    }

    for (i = 0u; i < (u32)st.research_count; ++i) {
        if (st.researches[i].state == (u8)D_RESEARCH_STATE_ACTIVE) {
            active = st.researches[i].id;
            break;
        }
    }

    for (i = 0u; i < (u32)st.research_count; ++i) {
        const d_research_progress *p = &st.researches[i];
        if (p->state != (u8)D_RESEARCH_STATE_PENDING) {
            continue;
        }
        if (best_any == 0u || p->id < best_any) {
            best_any = p->id;
        }
        if (active != 0u && p->id > active) {
            if (best_above == 0u || p->id < best_above) {
                best_above = p->id;
            }
        }
    }

    if (best_above != 0u) {
        target = best_above;
    } else if (best_any != 0u) {
        target = best_any;
    } else {
        return;
    }

    /* Route through deterministic net command stream. */
    {
        d_world *w = app->session().world();
        d_net_cmd cmd;
        unsigned char payload[32];
        u32 off = 0u;
        u32 tick;

        if (!w || !app->net().ready()) {
            return;
        }

        tick = w->tick_count + (app->net().input_delay_ticks() ? app->net().input_delay_ticks() : 1u);
        if (tick == 0u) {
            tick = 1u;
        }

        {
            u32 tag = (u32)D_NET_TLV_RESEARCH_ORG_ID;
            u32 len = 4u;
            u32 v = (u32)org_id;
            std::memcpy(payload + off, &tag, 4u); off += 4u;
            std::memcpy(payload + off, &len, 4u); off += 4u;
            std::memcpy(payload + off, &v, 4u);   off += 4u;
        }
        {
            u32 tag = (u32)D_NET_TLV_RESEARCH_ACTIVE_ID;
            u32 len = 4u;
            u32 v = (u32)target;
            std::memcpy(payload + off, &tag, 4u); off += 4u;
            std::memcpy(payload + off, &len, 4u); off += 4u;
            std::memcpy(payload + off, &v, 4u);   off += 4u;
        }

        std::memset(&cmd, 0, sizeof(cmd));
        cmd.schema_id = (u32)D_NET_SCHEMA_CMD_RESEARCH_V1;
        cmd.schema_ver = 1u;
        cmd.tick = tick;
        cmd.payload.ptr = payload;
        cmd.payload.len = off;

        (void)app->net().submit_cmd(&cmd);
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
        g_panel->layout_rect.h = d_q16_16_from_int(620);
        dui_widget_add_child(ctx.root, g_panel);

        g_hash_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_chunk_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_res_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_struct_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_pack_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_content_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_det_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_net_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_probe_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_env_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_hydro_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_volume_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_litho_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_machine_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_jobs_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_agents_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_throughput_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_org_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_econ_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);
        g_research_label = dui_widget_create(&ctx, DUI_WIDGET_LABEL);

        g_overlay_hydro_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        g_overlay_temp_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        g_overlay_pressure_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        g_overlay_volumes_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);
        g_research_next_button = dui_widget_create(&ctx, DUI_WIDGET_BUTTON);

        if (g_hash_label) dui_widget_add_child(g_panel, g_hash_label);
        if (g_chunk_label) dui_widget_add_child(g_panel, g_chunk_label);
        if (g_res_label) dui_widget_add_child(g_panel, g_res_label);
        if (g_struct_label) dui_widget_add_child(g_panel, g_struct_label);
        if (g_pack_label) dui_widget_add_child(g_panel, g_pack_label);
        if (g_content_label) dui_widget_add_child(g_panel, g_content_label);
        if (g_det_label) dui_widget_add_child(g_panel, g_det_label);
        if (g_net_label) dui_widget_add_child(g_panel, g_net_label);
        if (g_probe_label) dui_widget_add_child(g_panel, g_probe_label);
        if (g_env_label) dui_widget_add_child(g_panel, g_env_label);
        if (g_hydro_label) dui_widget_add_child(g_panel, g_hydro_label);
        if (g_volume_label) dui_widget_add_child(g_panel, g_volume_label);
        if (g_litho_label) dui_widget_add_child(g_panel, g_litho_label);
        if (g_machine_label) dui_widget_add_child(g_panel, g_machine_label);
        if (g_jobs_label) dui_widget_add_child(g_panel, g_jobs_label);
        if (g_agents_label) dui_widget_add_child(g_panel, g_agents_label);
        if (g_throughput_label) dui_widget_add_child(g_panel, g_throughput_label);
        if (g_org_label) dui_widget_add_child(g_panel, g_org_label);
        if (g_econ_label) dui_widget_add_child(g_panel, g_econ_label);
        if (g_research_label) dui_widget_add_child(g_panel, g_research_label);

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
        if (g_research_next_button) {
            g_research_next_button->text = "Set Active Research: Next";
            g_research_next_button->on_click = on_research_set_next;
            g_research_next_button->user_data = (void *)&app;
            dui_widget_add_child(g_panel, g_research_next_button);
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

static const char *net_role_text(d_net_role role) {
    switch (role) {
    case D_NET_ROLE_SINGLE: return "SINGLE";
    case D_NET_ROLE_HOST:   return "HOST";
    case D_NET_ROLE_CLIENT: return "CLIENT";
    default: break;
    }
    return "?";
}

static const char *job_state_text(d_job_state st) {
    switch (st) {
    case D_JOB_STATE_PENDING: return "PENDING";
    case D_JOB_STATE_ASSIGNED: return "ASSIGNED";
    case D_JOB_STATE_RUNNING: return "RUNNING";
    case D_JOB_STATE_COMPLETED: return "COMPLETED";
    case D_JOB_STATE_CANCELLED: return "CANCELLED";
    default: return "?";
    }
}

static const char *research_state_text(u8 st) {
    switch (st) {
    case D_RESEARCH_STATE_PENDING: return "PENDING";
    case D_RESEARCH_STATE_ACTIVE: return "ACTIVE";
    case D_RESEARCH_STATE_COMPLETED: return "COMPLETED";
    case D_RESEARCH_STATE_LOCKED: return "LOCKED";
    default: return "?";
    }
}

static q32_32 research_required_points_q32(const d_proto_research *r) {
    u32 off;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    q32_32 req = 0;

    if (!r || !r->cost.ptr || r->cost.len == 0u) {
        return 0;
    }
    off = 0u;
    while ((rc = d_tlv_kv_next(&r->cost, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_RESEARCH_COST_REQUIRED && payload.ptr && payload.len == 8u) {
            memcpy(&req, payload.ptr, sizeof(q32_32));
        }
    }
    return req;
}

static void buf_appendf(char *buf, size_t cap, size_t *pos, const char *fmt, ...) {
    va_list ap;
    int wrote;
    size_t avail;
    if (!buf || cap == 0u || !pos || !fmt) {
        return;
    }
    if (*pos >= cap) {
        return;
    }
    avail = cap - *pos;
    va_start(ap, fmt);
    wrote = std::vsnprintf(buf + *pos, avail, fmt, ap);
    va_end(ap);
    if (wrote <= 0) {
        return;
    }
    if ((size_t)wrote >= avail) {
        *pos = cap - 1u;
        buf[cap - 1u] = '\0';
        return;
    }
    *pos += (size_t)wrote;
}

static void update_org_research_econ(DomGameApp &app, d_world *w) {
    size_t pos;
    u32 org_count;
    d_org_id player_org;
    q32_32 balance = 0;
    u32 policy_count;

    (void)w;

    org_count = d_org_count();
    player_org = app.player_org_id();
    policy_count = d_content_policy_rule_count();

    if (player_org != 0u) {
        d_org o;
        if (d_org_get(player_org, &o) == 0 && o.account_id != 0u) {
            d_account a;
            if (d_account_get(o.account_id, &a) == 0) {
                balance = a.balance;
            }
        }
    }

    /* Orgs */
    g_buf_org[0] = '\0';
    pos = 0u;
    buf_appendf(g_buf_org, sizeof(g_buf_org), &pos,
                "Orgs: %u | player_org=%u | policy_rules=%u | balance=%lld",
                (unsigned)org_count,
                (unsigned)player_org,
                (unsigned)policy_count,
                (long long)(balance >> Q32_32_FRAC_BITS));
    if (g_org_label) {
        g_org_label->text = g_buf_org;
    }

    /* Econ */
    g_buf_econ[0] = '\0';
    pos = 0u;
    {
        u32 econ_count = d_econ_org_metrics_count();
        buf_appendf(g_buf_econ, sizeof(g_buf_econ), &pos, "Econ: %u", (unsigned)econ_count);
        if (player_org != 0u) {
            d_econ_org_metrics m;
            if (d_econ_get_org_metrics(player_org, &m) == 0) {
                buf_appendf(g_buf_econ, sizeof(g_buf_econ), &pos,
                            " | out=%lld in=%lld net=%lld idx=%lld",
                            (long long)(m.total_output >> Q32_32_FRAC_BITS),
                            (long long)(m.total_input >> Q32_32_FRAC_BITS),
                            (long long)(m.net_throughput >> Q32_32_FRAC_BITS),
                            (long long)(m.price_index >> Q32_32_FRAC_BITS));
            }
        }
    }
    if (g_econ_label) {
        g_econ_label->text = g_buf_econ;
    }

    /* Research */
    g_buf_research[0] = '\0';
    pos = 0u;
    buf_appendf(g_buf_research, sizeof(g_buf_research), &pos,
                "Research: %u | org=%u",
                (unsigned)d_content_research_count(),
                (unsigned)player_org);

    if (player_org != 0u) {
        d_research_org_state st;
        if (d_research_get_org_state(player_org, &st) == 0 && st.researches) {
            d_research_id active = 0u;
            u32 shown = 0u;
            u32 i;

            for (i = 0u; i < (u32)st.research_count; ++i) {
                if (st.researches[i].state == (u8)D_RESEARCH_STATE_ACTIVE) {
                    active = st.researches[i].id;
                    break;
                }
            }
            if (active != 0u) {
                const d_proto_research *rp = d_content_get_research(active);
                buf_appendf(g_buf_research, sizeof(g_buf_research), &pos,
                            " | active=%s",
                            (rp && rp->name) ? rp->name : "(node)");
            } else {
                buf_appendf(g_buf_research, sizeof(g_buf_research), &pos, " | active=(none)");
            }

            for (i = 0u; i < (u32)st.research_count && shown < 4u; ++i) {
                const d_research_progress *p = &st.researches[i];
                const d_proto_research *rp = d_content_get_research(p->id);
                q32_32 req = rp ? research_required_points_q32(rp) : 0;
                long long prog_i = (long long)(p->progress >> Q32_32_FRAC_BITS);
                long long req_i = (long long)(req >> Q32_32_FRAC_BITS);
                int pct = 0;
                if (req_i > 0) {
                    pct = (int)((prog_i * 100ll) / req_i);
                    if (pct < 0) pct = 0;
                    if (pct > 100) pct = 100;
                }
                buf_appendf(g_buf_research, sizeof(g_buf_research), &pos,
                            " | %s %s %lld/%lld (%d%%)",
                            (rp && rp->name) ? rp->name : "(node)",
                            research_state_text(p->state),
                            prog_i,
                            req_i,
                            pct);
                shown += 1u;
            }
        }
    }

    if (g_research_label) {
        g_research_label->text = g_buf_research;
    }
}

static void update_factory_inspectors(d_world *w) {
    u32 i;
    size_t pos;

    /* Machines */
    {
        u32 count = 0u;
        u32 shown = 0u;
        u32 scount;

        g_buf_machines[0] = '\0';
        scount = d_struct_count(w);
        for (i = 0u; i < scount; ++i) {
            const d_struct_instance *inst = d_struct_get_by_index(w, i);
            const d_proto_structure *sp = inst ? d_content_get_structure(inst->proto_id) : (const d_proto_structure *)0;
            if (!inst || !sp) continue;
            if ((sp->tags & D_TAG_STRUCTURE_MACHINE) == 0u) continue;
            count += 1u;
        }

        pos = 0u;
        buf_appendf(g_buf_machines, sizeof(g_buf_machines), &pos, "Machines: %u", (unsigned)count);
        for (i = 0u; i < scount && shown < 4u; ++i) {
            const d_struct_instance *inst = d_struct_get_by_index(w, i);
            const d_proto_structure *sp = inst ? d_content_get_structure(inst->proto_id) : (const d_proto_structure *)0;
            const d_proto_process *pp;
            int pct = 0;
            if (!inst || !sp) continue;
            if ((sp->tags & D_TAG_STRUCTURE_MACHINE) == 0u) continue;

            pp = (inst->machine.active_process_id != 0u) ? d_content_get_process(inst->machine.active_process_id) : (const d_proto_process *)0;
            if (pp && pp->base_duration > 0) {
                double p = d_q16_16_to_double(inst->machine.progress) / d_q16_16_to_double(pp->base_duration);
                if (p < 0.0) p = 0.0;
                if (p > 1.0) p = 1.0;
                pct = (int)(p * 100.0 + 0.5);
            }

            buf_appendf(g_buf_machines, sizeof(g_buf_machines), &pos,
                        " | #%u %s @(%d,%d) %s %d%%",
                        (unsigned)inst->id,
                        sp->name ? sp->name : "(struct)",
                        d_q16_16_to_int(inst->pos_x),
                        d_q16_16_to_int(inst->pos_y),
                        (pp && pp->name) ? pp->name : "(proc)",
                        pct);
            shown += 1u;
        }
        if (g_machine_label) {
            g_machine_label->text = g_buf_machines;
        }
    }

    /* Jobs */
    {
        u32 count = d_job_count(w);
        u32 shown = 0u;
        g_buf_jobs[0] = '\0';
        pos = 0u;
        buf_appendf(g_buf_jobs, sizeof(g_buf_jobs), &pos, "Jobs: %u", (unsigned)count);
        for (i = 0u; i < count && shown < 6u; ++i) {
            d_job_record jr;
            const d_proto_job_template *jt;
            if (d_job_get_by_index(w, i, &jr) != 0) continue;
            jt = d_content_get_job_template(jr.template_id);
            buf_appendf(g_buf_jobs, sizeof(g_buf_jobs), &pos,
                        " | #%u %s %s a=%u t=%u",
                        (unsigned)jr.id,
                        (jt && jt->name) ? jt->name : "(job)",
                        job_state_text(jr.state),
                        (unsigned)jr.assigned_agent,
                        (unsigned)jr.target_struct_eid);
            shown += 1u;
        }
        if (g_jobs_label) {
            g_jobs_label->text = g_buf_jobs;
        }
    }

    /* Agents */
    {
        u32 count = d_agent_count(w);
        u32 shown = 0u;
        g_buf_agents[0] = '\0';
        pos = 0u;
        buf_appendf(g_buf_agents, sizeof(g_buf_agents), &pos, "Agents: %u", (unsigned)count);
        for (i = 0u; i < count && shown < 6u; ++i) {
            d_agent_state a;
            i32 ax;
            i32 ay;
            if (d_agent_get_by_index(w, i, &a) != 0) continue;
            ax = (i32)(a.pos_x >> Q32_32_FRAC_BITS);
            ay = (i32)(a.pos_y >> Q32_32_FRAC_BITS);
            buf_appendf(g_buf_agents, sizeof(g_buf_agents), &pos,
                        " | #%u caps=0x%08x job=%u @(%d,%d)",
                        (unsigned)a.id,
                        (unsigned)a.caps.tags,
                        (unsigned)a.current_job,
                        (int)ax, (int)ay);
            shown += 1u;
        }
        if (g_agents_label) {
            g_agents_label->text = g_buf_agents;
        }
    }

    /* Throughput */
    {
        u32 count = d_sim_process_stats_count(w);
        u32 shown = 0u;
        g_buf_throughput[0] = '\0';
        pos = 0u;
        buf_appendf(g_buf_throughput, sizeof(g_buf_throughput), &pos, "Throughput: %u", (unsigned)count);
        for (i = 0u; i < count && shown < 6u; ++i) {
            d_sim_process_stats s;
            const d_proto_process *pp;
            u32 per_min = 0u;
            if (d_sim_process_stats_get_by_index(w, i, &s) != 0) continue;
            if (s.ticks_observed > 0u) {
                per_min = (u32)(((u64)s.output_units * 3600ull) / (u64)s.ticks_observed);
            }
            pp = d_content_get_process(s.process_id);
            buf_appendf(g_buf_throughput, sizeof(g_buf_throughput), &pos,
                        " | %s %u/min",
                        (pp && pp->name) ? pp->name : "(proc)",
                        (unsigned)per_min);
            shown += 1u;
        }
        if (g_throughput_label) {
            g_throughput_label->text = g_buf_throughput;
        }
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

    {
        const DomGameNet &net = app.net();
        const d_net_session &s = net.session();
        size_t pos = 0u;
        u16 shown = 0u;
        u16 i;

        g_buf_net[0] = '\0';
        buf_appendf(g_buf_net, sizeof(g_buf_net), &pos,
                    "Session: %s ready=%s sid=%u peer=%u tick=%u rate=%u delay=%u peers=%u",
                    net_role_text(s.role),
                    net.ready() ? "YES" : "NO",
                    (unsigned)s.id,
                    (unsigned)net.local_peer(),
                    (unsigned)s.tick,
                    (unsigned)s.tick_rate,
                    (unsigned)s.input_delay_ticks,
                    (unsigned)s.peer_count);
        if (s.peer_count > 0u && s.peers) {
            for (i = 0u; i < s.peer_count && shown < 8u; ++i) {
                const d_net_peer *p = &s.peers[i];
                buf_appendf(g_buf_net, sizeof(g_buf_net), &pos,
                            " | %u f=0x%08x ack=%u",
                            (unsigned)p->id,
                            (unsigned)p->flags,
                            (unsigned)p->last_ack_tick);
                shown += 1u;
            }
        }
        if (g_net_label) g_net_label->text = g_buf_net;
    }

    update_pack_info(inst);
    update_org_research_econ(app, w);
    update_factory_inspectors(w);
}

} // namespace dom
