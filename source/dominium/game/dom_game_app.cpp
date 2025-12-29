/*
FILE: source/dominium/game/dom_game_app.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_app
RESPONSIBILITY: Implements `dom_game_app`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_game_app.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "dom_game_states.h"
#include "dom_game_ui.h"
#include "dom_game_ui_debug.h"
#include "dom_game_save.h"
#include "dom_game_replay.h"
#include "dom_game_tools_build.h"
#include "dominium/version.h"
#include "dominium/paths.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/gfx.h"
#include "domino/system/d_system.h"
#include "system/d_system_input.h"
#include "env/d_env_field.h"
#include "env/d_env_volume.h"
#include "hydro/d_hydro.h"
#include "struct/d_struct.h"
#include "struct/d_struct_blueprint.h"
#include "trans/d_trans_mover.h"
#include "trans/d_trans_spline.h"
#include "res/d_res.h"
#include "content/d_content.h"
#include "ai/d_agent.h"
#include "net/d_net_apply.h"
#include "net/d_net_proto.h"
#include "net/d_net_transport.h"
}

struct DomNetReplayRecorder {
    d_replay_context *replay;
};

extern "C" void dom_net_replay_tick_observer(
    void            *user,
    struct d_world  *w,
    u32              tick,
    const d_net_cmd *cmds,
    u32              cmd_count
) {
    DomNetReplayRecorder *rec = (DomNetReplayRecorder *)user;
    std::vector<d_net_input_frame> inputs;
    std::vector<unsigned char *> bufs;
    u32 i;
    (void)w;

    if (!rec || !rec->replay || rec->replay->mode != DREPLAY_MODE_RECORD) {
        return;
    }
    if (!cmds || cmd_count == 0u) {
        return;
    }

    inputs.resize(static_cast<size_t>(cmd_count));
    bufs.resize(static_cast<size_t>(cmd_count), (unsigned char *)0);

    for (i = 0u; i < cmd_count; ++i) {
        unsigned cap = 2048u;
        unsigned char *buf = (unsigned char *)0;
        u32 out_size = 0u;
        int rc = -1;
        unsigned attempt;

        for (attempt = 0u; attempt < 6u; ++attempt) {
            buf = (unsigned char *)std::malloc(static_cast<size_t>(cap));
            if (!buf) {
                break;
            }
            rc = d_net_encode_cmd(&cmds[i], buf, (u32)cap, &out_size);
            if (rc == 0) {
                break;
            }
            std::free(buf);
            buf = (unsigned char *)0;
            if (rc != -2) {
                break;
            }
            cap *= 2u;
        }

        if (rc != 0 || !buf || out_size == 0u) {
            for (i = 0u; i < (u32)bufs.size(); ++i) {
                if (bufs[i]) {
                    std::free(bufs[i]);
                    bufs[i] = (unsigned char *)0;
                }
            }
            return;
        }

        bufs[i] = buf;
        std::memset(&inputs[i], 0, sizeof(inputs[i]));
        inputs[i].tick_index = cmds[i].tick;
        inputs[i].player_id = (u32)cmds[i].source_peer;
        inputs[i].payload_size = out_size;
        inputs[i].payload = (u8 *)buf;
    }

    (void)d_replay_record_frame(rec->replay,
                                tick,
                                &inputs[0],
                                cmd_count);

    for (i = 0u; i < (u32)bufs.size(); ++i) {
        if (bufs[i]) {
            std::free(bufs[i]);
            bufs[i] = (unsigned char *)0;
        }
    }
}

namespace dom {

namespace {

static const unsigned DEFAULT_TICK_RATE = 60u;

static unsigned make_version_u32(unsigned major, unsigned minor, unsigned patch) {
    return major * 10000u + minor * 100u + patch;
}

static unsigned suite_version_u32() {
    return make_version_u32(DOMINIUM_VERSION_MAJOR,
                            DOMINIUM_VERSION_MINOR,
                            DOMINIUM_VERSION_PATCH);
}

static bool is_dominium_repo_root(const std::string &root) {
    std::string repo = join(root, "repo");
    if (!dir_exists(repo)) {
        return false;
    }
    if (dir_exists(join(repo, "mods"))) {
        return true;
    }
    if (dir_exists(join(repo, "packs"))) {
        return true;
    }
    if (dir_exists(join(repo, "products"))) {
        return true;
    }
    return false;
}

static std::string find_dominium_home_from(const std::string &start) {
    std::string cur = start.empty() ? std::string(".") : start;
    for (unsigned i = 0u; i < 10u; ++i) {
        if (is_dominium_repo_root(cur)) {
            return cur;
        }
        cur = join(cur, "..");
    }
    return std::string();
}

static void apply_default_instance_values(InstanceInfo &inst) {
    inst.world_seed = 12345u;
    inst.world_size_m = 2048u;
    inst.vertical_min_m = -256;
    inst.vertical_max_m = 512;
    inst.suite_version = suite_version_u32();
    inst.core_version = suite_version_u32();
    inst.last_product = "game";
    inst.last_product_version = DOMINIUM_GAME_VERSION;
    inst.packs.clear();
    inst.mods.clear();
    {
        ModRef mref;
        mref.id = "base_demo";
        mref.version = 1u;
        inst.mods.push_back(mref);
    }
}

static d_structure_proto_id dom_find_structure_by_name(const char *name) {
    u32 i;
    u32 count = d_content_structure_count();
    if (!name) {
        return 0u;
    }
    for (i = 0u; i < count; ++i) {
        const d_proto_structure *sp = d_content_get_structure_by_index(i);
        if (sp && sp->name && std::strcmp(sp->name, name) == 0) {
            return sp->id;
        }
    }
    return 0u;
}

static d_spline_profile_id dom_find_spline_profile_by_name(const char *name) {
    u32 i;
    u32 count = d_content_spline_profile_count();
    if (!name) {
        return 0u;
    }
    for (i = 0u; i < count; ++i) {
        const d_proto_spline_profile *pp = d_content_get_spline_profile_by_index(i);
        if (pp && pp->name && std::strcmp(pp->name, name) == 0) {
            return pp->id;
        }
    }
    return 0u;
}

static unsigned char dom_clamp_u8(int v) {
    if (v < 0) {
        return 0u;
    }
    if (v > 255) {
        return 255u;
    }
    return (unsigned char)v;
}

static void dom_emit_rect(d_gfx_cmd_buffer *buf, int x, int y, int w, int h, d_gfx_color color) {
    d_gfx_draw_rect_cmd r;
    if (!buf) {
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
    if (w <= 0 || h <= 0) {
        return;
    }
    dom_emit_rect(buf, x, y, w, thickness, color);
    dom_emit_rect(buf, x, y + h - thickness, w, thickness, color);
    dom_emit_rect(buf, x, y, thickness, h, color);
    dom_emit_rect(buf, x + w - thickness, y, thickness, h, color);
}

static q16_16 dom_find_env_field0(const d_env_sample *samples, u16 count, d_env_field_id field_id) {
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

static void dom_draw_debug_overlays(const DomGameApp &app,
                                    d_world *w,
                                    d_gfx_cmd_buffer *cmd_buffer,
                                    i32 width,
                                    i32 height) {
    GameCamera cam;
    double zoom;
    double px_per_unit;
    int cell_px;
    u32 i;

    if (!w || !cmd_buffer) {
        return;
    }
    if (!app.overlay_hydrology() &&
        !app.overlay_temperature() &&
        !app.overlay_pressure() &&
        !app.overlay_volumes()) {
        return;
    }

    cam = app.camera();
    zoom = (double)cam.zoom;
    if (zoom < 1.0) zoom = 1.0;
    px_per_unit = 32.0 * (50.0 / zoom);
    if (px_per_unit < 2.0) px_per_unit = 2.0;
    if (px_per_unit > 96.0) px_per_unit = 96.0;

    cell_px = (int)(px_per_unit + 0.5);
    if (cell_px < 2) cell_px = 2;

    for (i = 0u; i < w->chunk_count; ++i) {
        const d_chunk *chunk = &w->chunks[i];
        double dx = (double)chunk->cx - (double)cam.cx;
        double dy = (double)chunk->cy - (double)cam.cy;
        int x0 = (int)((double)width * 0.5 + dx * px_per_unit);
        int y0 = (int)((double)height * 0.5 + dy * px_per_unit);

        if (x0 + cell_px < 0 || y0 + cell_px < 0 || x0 >= width || y0 >= height) {
            continue;
        }

        if (app.overlay_hydrology()) {
            d_hydro_cell hc;
            q32_32 sx = (((q32_32)chunk->cx) << Q32_32_FRAC_BITS) + ((q32_32)1 << 31);
            q32_32 sy = (((q32_32)chunk->cy) << Q32_32_FRAC_BITS) + ((q32_32)1 << 31);
            q32_32 sz = 0;
            d_gfx_color c;

            std::memset(&hc, 0, sizeof(hc));
            (void)d_hydro_sample_at(w, sx, sy, sz, &hc);
            {
                int depth_u8 = (int)(hc.depth >> 8);
                unsigned char b = dom_clamp_u8(depth_u8);
                c.a = 0xffu;
                c.r = 0x00u;
                c.g = (unsigned char)(b / 3u);
                c.b = b;
            }
            dom_emit_rect(cmd_buffer, x0, y0, cell_px, cell_px, c);
        } else if (app.overlay_temperature() || app.overlay_pressure()) {
            d_env_sample samples[16];
            u16 count;
            q32_32 sx = (((q32_32)chunk->cx) << Q32_32_FRAC_BITS) + ((q32_32)1 << 31);
            q32_32 sy = (((q32_32)chunk->cy) << Q32_32_FRAC_BITS) + ((q32_32)1 << 31);
            q32_32 sz = 0;
            d_gfx_color c;

            count = d_env_sample_exterior_at(w, sx, sy, sz, samples, 16u);
            if (app.overlay_temperature()) {
                q16_16 t = dom_find_env_field0(samples, count, D_ENV_FIELD_TEMPERATURE);
                int ti = d_q16_16_to_int(t);
                int tmin = -1024;
                int tmax = 128;
                int norm;
                if (ti < tmin) ti = tmin;
                if (ti > tmax) ti = tmax;
                norm = (ti - tmin) * 255 / (tmax - tmin);
                c.a = 0xffu;
                c.r = dom_clamp_u8(norm);
                c.g = 0x00u;
                c.b = dom_clamp_u8(255 - norm);
            } else {
                q16_16 p = dom_find_env_field0(samples, count, D_ENV_FIELD_PRESSURE);
                int pi = d_q16_16_to_int(p);
                int pmin = -512;
                int pmax = 256;
                int norm;
                if (pi < pmin) pi = pmin;
                if (pi > pmax) pi = pmax;
                norm = (pi - pmin) * 255 / (pmax - pmin);
                c.a = 0xffu;
                c.r = dom_clamp_u8(norm);
                c.g = dom_clamp_u8(norm);
                c.b = dom_clamp_u8((255 - norm) / 2);
            }
            dom_emit_rect(cmd_buffer, x0, y0, cell_px, cell_px, c);
        }
    }

    if (app.overlay_volumes()) {
        q32_32 px;
        q32_32 py;
        q32_32 pz;
        d_env_volume_id pinned;
        u32 vcount;
        u32 vi;
        app.debug_probe_world_coords(&px, &py, &pz);
        pinned = d_env_volume_find_at(w, px, py, pz);

        vcount = d_env_volume_count(w);
        for (vi = 0u; vi < vcount; ++vi) {
            const d_env_volume *vol = d_env_volume_get_by_index(w, vi);
            if (!vol) {
                continue;
            }
            if (pz < vol->min_z || pz > vol->max_z) {
                continue;
            }

            {
                double min_x = (double)vol->min_x / 4294967296.0;
                double min_y = (double)vol->min_y / 4294967296.0;
                double max_x = (double)vol->max_x / 4294967296.0;
                double max_y = (double)vol->max_y / 4294967296.0;

                int x0 = (int)((double)width * 0.5 + (min_x - (double)cam.cx) * px_per_unit);
                int y0 = (int)((double)height * 0.5 + (min_y - (double)cam.cy) * px_per_unit);
                int x1 = (int)((double)width * 0.5 + (max_x - (double)cam.cx) * px_per_unit);
                int y1 = (int)((double)height * 0.5 + (max_y - (double)cam.cy) * px_per_unit);
                int rw = x1 - x0;
                int rh = y1 - y0;
                d_gfx_color c;
                if (rw <= 0 || rh <= 0) {
                    continue;
                }
                if (vol->id == pinned) {
                    c.a = 0xffu;
                    c.r = 0xffu;
                    c.g = 0xe0u;
                    c.b = 0x40u;
                } else {
                    c.a = 0xffu;
                    c.r = 0x40u;
                    c.g = 0xffu;
                    c.b = 0x40u;
                }
                dom_emit_outline_rect(cmd_buffer, x0, y0, rw, rh, 2, c);
            }
        }
    }
}

static void dom_draw_trans_overlays(const DomGameApp &app,
                                   d_world *w,
                                   d_gfx_cmd_buffer *cmd_buffer,
                                   i32 width,
                                   i32 height) {
    GameCamera cam;
    double px_per_unit;
    u32 i;
    u32 seg_count;

    if (!w || !cmd_buffer) {
        return;
    }

    cam = app.camera();
    px_per_unit = 32.0 * (50.0 / (double)cam.zoom);
    if (px_per_unit < 2.0) px_per_unit = 2.0;
    if (px_per_unit > 96.0) px_per_unit = 96.0;

    /* Draw structure markers. */
    {
        u32 scount = d_struct_count(w);
        d_gfx_color c;
        c.a = 0xffu; c.r = 0x80u; c.g = 0x80u; c.b = 0x80u;
        for (i = 0u; i < scount; ++i) {
            const d_struct_instance *inst = d_struct_get_by_index(w, i);
            if (!inst) continue;
            {
                double wx = d_q16_16_to_double(inst->pos_x);
                double wy = d_q16_16_to_double(inst->pos_y);
                int sx = (int)((double)width * 0.5 + (wx - (double)cam.cx) * px_per_unit);
                int sy = (int)((double)height * 0.5 + (wy - (double)cam.cy) * px_per_unit);
                dom_emit_outline_rect(cmd_buffer, sx - 6, sy - 6, 12, 12, 2, c);
            }
        }
    }

    /* Draw splines as polylines. */
    {
        u32 spline_count = d_trans_spline_count(w);
        for (i = 0u; i < spline_count; ++i) {
            d_spline_instance s;
            d_spline_node nodes[32];
            u16 node_count = 0u;
            u16 n;
            dgfx_line_segment_t segs[31];
            u32 color = 0xffaaaaaaU;

            if (d_trans_spline_get_by_index(w, i, &s) != 0) {
                continue;
            }
            if (d_trans_spline_copy_nodes(w,
                                          s.node_start_index,
                                          s.node_count,
                                          nodes,
                                          (u16)(sizeof(nodes) / sizeof(nodes[0])),
                                          &node_count) != 0) {
                continue;
            }
            if (node_count < 2u) {
                continue;
            }

            {
                const d_proto_spline_profile *pp = d_content_get_spline_profile(s.profile_id);
                if (pp) {
                    if (pp->type == (u16)D_SPLINE_TYPE_ITEM) {
                        color = 0xffffaa00U;
                    } else if (pp->type == (u16)D_SPLINE_TYPE_VEHICLE) {
                        color = 0xff00ffaaU;
                    } else if (pp->type == (u16)D_SPLINE_TYPE_FLUID) {
                        color = 0xff00aaffU;
                    }
                }
            }

            seg_count = 0u;
            for (n = 0u; n + 1u < node_count && seg_count < (u32)(sizeof(segs) / sizeof(segs[0])); ++n) {
                double x0 = (double)nodes[n].x / 4294967296.0;
                double y0 = (double)nodes[n].y / 4294967296.0;
                double x1 = (double)nodes[n + 1u].x / 4294967296.0;
                double y1 = (double)nodes[n + 1u].y / 4294967296.0;

                segs[seg_count].x0 = (i32)((double)width * 0.5 + (x0 - (double)cam.cx) * px_per_unit);
                segs[seg_count].y0 = (i32)((double)height * 0.5 + (y0 - (double)cam.cy) * px_per_unit);
                segs[seg_count].x1 = (i32)((double)width * 0.5 + (x1 - (double)cam.cx) * px_per_unit);
                segs[seg_count].y1 = (i32)((double)height * 0.5 + (y1 - (double)cam.cy) * px_per_unit);
                segs[seg_count].color_rgba = color;
                segs[seg_count].thickness = 2;
                seg_count++;
            }

            if (seg_count > 0u) {
                (void)dgfx_cmd_emit((dgfx_cmd_buffer *)cmd_buffer,
                                    (u16)DGFX_CMD_DRAW_LINES,
                                    segs,
                                    (u16)(seg_count * sizeof(segs[0])));
            }
        }
    }

    /* Draw movers as simple glyphs. */
    {
        u32 mover_count = d_trans_mover_count(w);
        for (i = 0u; i < mover_count; ++i) {
            d_mover m;
            q32_32 wx = 0;
            q32_32 wy = 0;
            q32_32 wz = 0;
            d_gfx_color c;

            if (d_trans_mover_get_by_index(w, i, &m) != 0) {
                continue;
            }
            if (d_trans_spline_sample_pos(w, m.spline_id, m.param, &wx, &wy, &wz) != 0) {
                continue;
            }

            c.a = 0xffu;
            c.r = 0xffu;
            c.g = 0xffu;
            c.b = 0xffu;
            if (m.kind == D_MOVER_KIND_ITEM) {
                c.r = 0xffu; c.g = 0xffu; c.b = 0x40u;
            } else if (m.kind == D_MOVER_KIND_CONTAINER) {
                c.r = 0xffu; c.g = 0x80u; c.b = 0xffu;
            } else if (m.kind == D_MOVER_KIND_VEHICLE) {
                c.r = 0x40u; c.g = 0xffu; c.b = 0x40u;
            } else if (m.kind == D_MOVER_KIND_FLUID_PACKET) {
                c.r = 0x40u; c.g = 0xa0u; c.b = 0xffu;
            }

            {
                double x = (double)wx / 4294967296.0;
                double y = (double)wy / 4294967296.0;
                int sx = (int)((double)width * 0.5 + (x - (double)cam.cx) * px_per_unit);
                int sy = (int)((double)height * 0.5 + (y - (double)cam.cy) * px_per_unit);
                dom_emit_rect(cmd_buffer, sx - 3, sy - 3, 6, 6, c);
            }
        }
    }
}

} // namespace

DomGameApp::DomGameApp()
    : m_mode(GAME_MODE_GUI),
      m_server_mode(SERVER_OFF),
      m_demo_mode(false),
      m_connect_addr(),
      m_net_port(0u),
      m_compat_read_only(false),
      m_compat_limited(false),
      m_tick_rate_hz(DEFAULT_TICK_RATE),
      m_main_view_id(0),
      m_state_id(GAME_STATE_BOOT),
      m_state(0),
      m_running(false),
      m_mouse_x(0),
      m_mouse_y(0),
      m_last_struct_id(0),
      m_player_org_id(0u),
      m_dev_mode(false),
      m_detmode(0u),
      m_last_hash(0u),
      m_replay_last_tick(0u),
      m_net_replay_user(0),
      m_runtime(0),
      m_last_wall_us(0u),
      m_show_debug_panel(false),
      m_debug_probe_set(false),
      m_debug_probe_x(0),
      m_debug_probe_y(0),
      m_debug_probe_z(0),
      m_show_overlay_hydro(false),
      m_show_overlay_temp(false),
      m_show_overlay_pressure(false),
      m_show_overlay_volumes(false) {
    std::memset(&m_ui_ctx, 0, sizeof(m_ui_ctx));
    std::memset(m_hud_instance_text, 0, sizeof(m_hud_instance_text));
    std::memset(m_hud_remaining_text, 0, sizeof(m_hud_remaining_text));
    std::memset(m_hud_inventory_text, 0, sizeof(m_hud_inventory_text));
}

DomGameApp::~DomGameApp() {
    shutdown();
}

bool DomGameApp::init_from_cli(const dom_game_config &cfg) {
    shutdown();

    m_mode = static_cast<GameMode>(cfg.mode);
    m_server_mode = static_cast<ServerMode>(cfg.server_mode);
    m_demo_mode = (cfg.demo_mode != 0u);
    m_connect_addr = cfg.connect_addr;
    m_net_port = cfg.net_port;
    m_tick_rate_hz = cfg.tick_rate_hz ? cfg.tick_rate_hz : DEFAULT_TICK_RATE;
    m_compat_read_only = false;
    m_compat_limited = false;
    m_dev_mode = (cfg.dev_mode != 0u);
    m_detmode = cfg.deterministic_test ? 3u : 0u;
    m_replay_record_path = cfg.replay_record_path;
    m_replay_play_path = cfg.replay_play_path;
    m_show_debug_panel = m_dev_mode;
    m_last_hash = 0u;
    if (!m_replay_record_path.empty()) {
        m_detmode = 1u;
    }
    if (!m_replay_play_path.empty()) {
        m_detmode = 2u;
    }

    if (!init_paths(cfg)) {
        std::printf("DomGameApp: failed to resolve paths\n");
        return false;
    }
    if (!load_instance(cfg)) {
        std::printf("DomGameApp: failed to load instance '%s'\n",
                    m_instance.id.c_str());
        return false;
    }
    if (!evaluate_compatibility(cfg)) {
        std::printf("DomGameApp: compatibility check failed\n");
        return false;
    }

    {
        const char *sys_backend = (cfg.platform_backend[0] == '\0') ? "win32" : cfg.platform_backend;
        std::printf("DomGameApp: initializing system backend '%s'\n", sys_backend);
        if (!d_system_init(sys_backend)) {
            std::printf("DomGameApp: system init failed\n");
            return false;
        }
    }

    if (m_mode != GAME_MODE_HEADLESS) {
        const char *gfx_backend = (cfg.gfx_backend[0] == '\0') ? "soft" : cfg.gfx_backend;
        std::printf("DomGameApp: initializing gfx backend '%s'\n", gfx_backend);
        if (!d_gfx_init(gfx_backend)) {
            std::printf("DomGameApp: gfx init failed\n");
            return false;
        }
    }

    if (!init_session(cfg)) {
        std::printf("DomGameApp: session init failed\n");
        return false;
    }
    if (!init_views_and_ui(cfg)) {
        std::printf("DomGameApp: view/UI init failed\n");
        return false;
    }

    {
        const bool auto_start = (cfg.server_mode != DOM_GAME_SERVER_OFF) || (cfg.connect_addr[0] != '\0') ||
                                (cfg.mode == DOM_GAME_MODE_HEADLESS);
        m_state_id = auto_start ? GAME_STATE_LOADING : GAME_STATE_BOOT;
    }
    m_state = create_state(m_state_id);
    if (!m_state) {
        return false;
    }
    m_state->on_enter(*this);

    m_running = true;
    return true;
}

void DomGameApp::run() {
    if (!m_running) {
        return;
    }
    m_last_wall_us = dsys_time_now_us();
    main_loop();
}

void DomGameApp::shutdown() {
    if (m_state) {
        m_state->on_exit(*this);
        destroy_state(m_state);
        m_state = 0;
    }

    if (m_main_view_id != 0u) {
        d_view_destroy(m_main_view_id);
        m_main_view_id = 0u;
    }

    dui_shutdown_context(&m_ui_ctx);

    /* Flush replay recording before shutting down the session (which frees replay state). */
    if (!m_replay_record_path.empty() && m_session.replay() &&
        m_session.replay()->mode == DREPLAY_MODE_RECORD) {
        if (!game_save_replay(m_session.replay(), m_replay_record_path)) {
            std::printf("DomGameApp: failed to write replay '%s'\n", m_replay_record_path.c_str());
        }
    }

    d_net_set_tick_cmds_observer((d_net_tick_cmds_observer_fn)0, (void *)0);
    if (m_net_replay_user) {
        delete (struct DomNetReplayRecorder *)m_net_replay_user;
        m_net_replay_user = 0;
    }
    m_replay_last_tick = 0u;

    if (m_runtime) {
        dom_game_runtime_destroy(m_runtime);
        m_runtime = 0;
    }
    m_last_wall_us = 0u;

    m_net.shutdown();
    m_session.shutdown();
    d_gfx_shutdown();
    d_system_shutdown();

    m_running = false;
}

void DomGameApp::request_state_change(GameStateId next) {
    change_state(next);
}

void DomGameApp::request_exit() {
    m_running = false;
}

bool DomGameApp::init_paths(const dom_game_config &cfg) {
    std::string home = cfg.dominium_home;
    const char *env_home;

    if (home.empty()) {
        env_home = std::getenv("DOMINIUM_HOME");
        if (env_home && env_home[0] != '\0') {
            home = env_home;
        }
    }
    if (home.empty()) {
        home = find_dominium_home_from(".");
        if (home.empty()) {
            const char *install_root = dmn_get_install_root();
            if (install_root && install_root[0] != '\0') {
                home = find_dominium_home_from(install_root);
            }
        }
    }
    if (home.empty()) {
        home = ".";
    }
    return resolve_paths(m_paths, home);
}

bool DomGameApp::load_instance(const dom_game_config &cfg) {
    m_instance.id = cfg.instance_id[0] ? cfg.instance_id : "demo";

    if (!m_instance.load(m_paths)) {
        apply_default_instance_values(m_instance);
        if (!m_instance.save(m_paths)) {
            std::printf("DomGameApp: created default instance '%s' (unsaved)\n",
                        m_instance.id.c_str());
        }
    }
    return true;
}

bool DomGameApp::evaluate_compatibility(const dom_game_config &cfg) {
    ProductInfo prod;
    CompatResult res;

    prod.product = "game";
    if (cfg.connect_addr[0] != '\0') {
        prod.role_detail = "client";
    } else if (cfg.server_mode != DOM_GAME_SERVER_OFF) {
        prod.role_detail = "server";
    } else {
        prod.role_detail = "client";
    }
    prod.product_version = suite_version_u32();
    prod.core_version = suite_version_u32();
    prod.suite_version = suite_version_u32();

    res = evaluate_compat(prod, m_instance);
    if (res == COMPAT_INCOMPATIBLE || res == COMPAT_MOD_UNSAFE || res == COMPAT_SCHEMA_MISMATCH) {
        return false;
    }
    m_compat_read_only = (res == COMPAT_READONLY);
    m_compat_limited = (res == COMPAT_LIMITED);
    return true;
}

bool DomGameApp::init_session(const dom_game_config &cfg) {
    SessionConfig scfg;
    scfg.platform_backend = cfg.platform_backend;
    scfg.gfx_backend = cfg.gfx_backend;
    scfg.audio_backend = std::string();
    scfg.headless = (cfg.mode == DOM_GAME_MODE_HEADLESS);
    scfg.tui = (cfg.mode == DOM_GAME_MODE_TUI);
    if (!m_session.init(m_paths, m_instance, scfg)) {
        return false;
    }

    /* Reset any previous net replay hook. */
    d_net_set_tick_cmds_observer((d_net_tick_cmds_observer_fn)0, (void *)0);
    if (m_net_replay_user) {
        delete (struct DomNetReplayRecorder *)m_net_replay_user;
        m_net_replay_user = 0;
    }
    m_replay_last_tick = 0u;

    /* Choose/create a default org for ownership + research (demo/product-side). */
    m_player_org_id = 0u;
    {
        u32 org_count = d_org_count();
        if (org_count == 0u) {
            m_player_org_id = d_org_create((q32_32)0);
        } else {
            d_org o;
            if (d_org_get_by_index(0u, &o) == 0) {
                m_player_org_id = o.id;
            }
        }
    }

    /* Replay integration: record or playback command stream. */
    if (!m_replay_play_path.empty()) {
        if (!game_load_replay(m_replay_play_path, m_session.replay())) {
            std::printf("DomGameApp: failed to load replay '%s'\n", m_replay_play_path.c_str());
            return false;
        }
        m_replay_last_tick = game_replay_last_tick(m_session.replay());
        (void)d_net_cmd_queue_init();
    } else if (!m_replay_record_path.empty()) {
        if (d_replay_init_record(m_session.replay(), 1024u) != 0) {
            std::printf("DomGameApp: failed to init replay record\n");
            return false;
        }
        {
            struct DomNetReplayRecorder *rec = new DomNetReplayRecorder();
            rec->replay = m_session.replay();
            m_net_replay_user = rec;
            d_net_set_tick_cmds_observer(dom_net_replay_tick_observer, rec);
        }
    }

    /* Network roles: client, host/listen, or single. */
    if (m_session.replay() && m_session.replay()->mode == DREPLAY_MODE_PLAYBACK) {
        if (!m_net.init_single(m_tick_rate_hz)) {
            return false;
        }
    } else if (cfg.connect_addr[0] != '\0') {
        if (!m_net.init_client(m_tick_rate_hz, cfg.connect_addr)) {
            return false;
        }
    } else if (cfg.server_mode == DOM_GAME_SERVER_LISTEN) {
        if (!m_net.init_listen(m_tick_rate_hz, cfg.net_port)) {
            return false;
        }
    } else if (cfg.server_mode == DOM_GAME_SERVER_DEDICATED) {
        if (!m_net.init_dedicated(m_tick_rate_hz, cfg.net_port)) {
            return false;
        }
    } else {
        if (!m_net.init_single(m_tick_rate_hz)) {
            return false;
        }
    }

    if (m_runtime) {
        dom_game_runtime_destroy(m_runtime);
        m_runtime = 0;
    }

    {
        dom_game_runtime_init_desc rdesc;
        std::memset(&rdesc, 0, sizeof(rdesc));
        rdesc.struct_size = sizeof(rdesc);
        rdesc.struct_version = DOM_GAME_RUNTIME_INIT_DESC_VERSION;
        rdesc.session = &m_session;
        rdesc.net = &m_net;
        rdesc.instance = &m_instance;
        rdesc.ups = m_tick_rate_hz;

        m_runtime = dom_game_runtime_create(&rdesc);
        if (!m_runtime) {
            return false;
        }
        if (m_replay_last_tick > 0u) {
            (void)dom_game_runtime_set_replay_last_tick(m_runtime, m_replay_last_tick);
        }
        m_last_wall_us = 0u;
    }

    ensure_demo_agents();
    return true;
}

bool DomGameApp::init_views_and_ui(const dom_game_config &cfg) {
    d_view_desc desc;
    (void)cfg;

    std::memset(&desc, 0, sizeof(desc));
    desc.id = 1u;
    desc.vp_x = d_q16_16_from_int(0);
    desc.vp_y = d_q16_16_from_int(0);
    desc.vp_w = d_q16_16_from_int(1);
    desc.vp_h = d_q16_16_from_int(1);
    desc.camera.pos_x = d_q16_16_from_int(0);
    desc.camera.pos_y = d_q16_16_from_int(10);
    desc.camera.pos_z = d_q16_16_from_int(0);
    desc.camera.dir_x = 0;
    desc.camera.dir_y = d_q16_16_from_int(-1);
    desc.camera.dir_z = 0;
    desc.camera.up_x = 0;
    desc.camera.up_y = 0;
    desc.camera.up_z = d_q16_16_from_int(1);

    m_main_view_id = d_view_create(&desc);
    if (m_main_view_id == 0u) {
        return false;
    }

    dui_shutdown_context(&m_ui_ctx);
    dui_init_context(&m_ui_ctx);
    dom_game_ui_set_app(this);

    dom_game_ui_build_root(m_ui_ctx, m_mode);
    m_camera.reset();
    return true;
}

void DomGameApp::ensure_demo_agents() {
    d_world *w = world();
    u32 i;
    if (!w) {
        return;
    }
    if (dom_find_structure_by_name("Demo Extractor") == 0u) {
        return;
    }
    if (d_agent_count(w) != 0u) {
        return;
    }

    for (i = 0u; i < 4u; ++i) {
        d_agent_state a;
        std::memset(&a, 0, sizeof(a));
        a.owner_eid = 0u;
        a.owner_org = m_player_org_id;
        a.caps.tags = (d_content_tag)(D_TAG_CAP_WALK | D_TAG_CAP_OPERATE_PROCESS);
        a.caps.max_speed = d_q16_16_from_int(1);
        a.caps.max_carry_mass = d_q16_16_from_int(100);
        a.current_job = 0u;
        a.pos_x = ((q32_32)(i64)(i)) << Q32_32_FRAC_BITS;
        a.pos_y = 0;
        a.pos_z = 0;
        a.flags = D_AGENT_FLAG_IDLE;
        (void)d_agent_register(w, &a);
    }
}

void DomGameApp::main_loop() {
    const unsigned sleep_ms = (m_tick_rate_hz > 0u) ? (1000u / m_tick_rate_hz) : 0u;

    while (m_running) {
        if (d_system_pump_events() != 0) {
            m_running = false;
            break;
        }
        tick_fixed();
        if (!m_running) {
            break;
        }
        if (m_mode != GAME_MODE_HEADLESS) {
            render_frame();
        }
        if (sleep_ms > 0u) {
            d_system_sleep_ms(sleep_ms);
        }
    }
}

void DomGameApp::tick_fixed() {
    const u64 now_us = dsys_time_now_us();
    const u64 dt_us = (m_last_wall_us > 0u && now_us >= m_last_wall_us) ? (now_us - m_last_wall_us) : 0u;
    m_last_wall_us = now_us;

    process_input_events();
    update_camera();

    if (m_session.is_initialized() && m_runtime) {
        (void)dom_game_runtime_pump(m_runtime);
    }

    if (m_state) {
        m_state->tick(*this);
    }

    if (m_session.is_initialized() && m_state_id == GAME_STATE_RUNNING && m_runtime) {
        u32 stepped = 0u;
        const int rc = dom_game_runtime_tick_wall(m_runtime, dt_us, &stepped);
        if (rc == DOM_GAME_RUNTIME_REPLAY_END || rc == DOM_GAME_RUNTIME_ERR) {
            request_exit();
            return;
        }
    }
    update_demo_hud();
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
    update_debug_panel();
}

void DomGameApp::render_frame() {
    d_view_desc *view = d_view_get(m_main_view_id);
    d_gfx_cmd_buffer *cmd_buffer;
    d_view_frame frame;
    dui_rect root_rect;
    i32 width = 800;
    i32 height = 600;

    if (!view) {
        return;
    }

    cmd_buffer = d_gfx_cmd_buffer_begin();
    if (!cmd_buffer) {
        return;
    }

    frame.view = view;
    frame.cmd_buffer = cmd_buffer;

    d_gfx_get_surface_size(&width, &height);

    root_rect.x = 0;
    root_rect.y = 0;
    root_rect.w = d_q16_16_from_int(width);
    root_rect.h = d_q16_16_from_int(height);

    d_view_render(world(), view, &frame);
    dom_draw_debug_overlays(*this, world(), cmd_buffer, width, height);
    dom_draw_trans_overlays(*this, world(), cmd_buffer, width, height);
    m_build_tool.render_overlay(*this, cmd_buffer, width, height);
    dui_layout(&m_ui_ctx, &root_rect);
    dui_render(&m_ui_ctx, &frame);

    d_gfx_cmd_buffer_end(cmd_buffer);
    d_gfx_submit(cmd_buffer);
    d_gfx_present();
}

void DomGameApp::change_state(GameStateId next) {
    if (m_state_id == next && m_state) {
        return;
    }

    if (m_state) {
        m_state->on_exit(*this);
        destroy_state(m_state);
        m_state = 0;
    }

    m_state_id = next;
    m_state = create_state(next);
    if (m_state) {
        m_state->on_enter(*this);
    }
}

void DomGameApp::process_input_events() {
    d_sys_event ev;
    while (d_system_poll_event(&ev) > 0) {
        int build_consumed = 0;
        if (ev.type == D_SYS_EVENT_QUIT) {
            m_running = false;
            break;
        }
        if (ev.type == D_SYS_EVENT_MOUSE_MOVE) {
            m_mouse_x = ev.u.mouse.x;
            m_mouse_y = ev.u.mouse.y;
            m_build_tool.set_mouse_pos(m_mouse_x, m_mouse_y);
        }
        if (ev.type == D_SYS_EVENT_MOUSE_BUTTON_DOWN) {
            m_mouse_x = ev.u.mouse.x;
            m_mouse_y = ev.u.mouse.y;
            m_build_tool.set_mouse_pos(m_mouse_x, m_mouse_y);
            int handled = dom_game_ui_try_click(m_ui_ctx, m_mouse_x, m_mouse_y);
            if (!handled) {
                handled = m_build_tool.handle_event(*this, ev);
            }
            if (!handled && m_show_debug_panel) {
                if (ev.u.mouse.button == 1u) {
                    i32 width = 800;
                    i32 height = 600;
                    GameCamera cam = camera();
                    double zoom = (double)cam.zoom;
                    double px_per_unit;
                    double wx;
                    double wy;
                    q16_16 x16;
                    q16_16 y16;

                    d_gfx_get_surface_size(&width, &height);
                    if (zoom < 1.0) zoom = 1.0;
                    px_per_unit = 32.0 * (50.0 / zoom);
                    if (px_per_unit < 2.0) px_per_unit = 2.0;

                    wx = (double)cam.cx + ((double)m_mouse_x - (double)width * 0.5) / px_per_unit;
                    wy = (double)cam.cy + ((double)m_mouse_y - (double)height * 0.5) / px_per_unit;

                    x16 = d_q16_16_from_double(wx);
                    y16 = d_q16_16_from_double(wy);
                    set_debug_probe(((q32_32)x16) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS),
                                    ((q32_32)y16) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS),
                                    0);
                } else if (ev.u.mouse.button == 2u) {
                    clear_debug_probe();
                }
            }
        }
        if (ev.type == D_SYS_EVENT_KEY_DOWN || ev.type == D_SYS_EVENT_KEY_UP) {
            if (ev.u.key.key == D_SYS_KEY_ESCAPE && ev.type == D_SYS_EVENT_KEY_DOWN) {
                m_running = false;
            }
            if (ev.type == D_SYS_EVENT_KEY_DOWN) {
                build_consumed = m_build_tool.handle_event(*this, ev);
            }
        }
        if (!build_consumed) {
            m_camera.handle_input(ev);
        } else if (ev.type == D_SYS_EVENT_KEY_UP) {
            m_camera.handle_input(ev);
        }
    }
}

void DomGameApp::update_camera() {
    float tick_dt = (m_tick_rate_hz > 0u) ? (1.0f / (float)m_tick_rate_hz) : (1.0f / 60.0f);
    d_view_desc *view = d_view_get(m_main_view_id);
    m_camera.tick(tick_dt);
    if (view) {
        m_camera.apply_to_view(*view);
    }
}

void DomGameApp::spawn_demo_blueprint() {
    d_world *w = world();
    const d_proto_blueprint *bp;
    q16_16 pos_x;
    q16_16 pos_y;
    if (!w) {
        return;
    }
    bp = d_content_get_blueprint_by_name("Demo Extractor Kit");
    if (!bp) {
        return;
    }
    pos_x = d_q16_16_from_double((double)m_camera.cx);
    pos_y = d_q16_16_from_double((double)m_camera.cy);
    {
        int id = d_struct_spawn_blueprint(w, bp, pos_x, pos_y, d_q16_16_from_int(0));
        if (id > 0) {
            m_last_struct_id = (d_struct_instance_id)id;
            {
                d_struct_instance *inst = d_struct_get_mutable(w, (d_struct_instance_id)id);
                if (inst) {
                    inst->owner_org = m_player_org_id;
                }
            }
        }
    }
}

void DomGameApp::update_demo_hud() {
    d_world *w = world();
    const d_struct_instance *inst = (const d_struct_instance *)0;
    d_struct_instance_id current = m_last_struct_id;
    if (!w || m_state_id != GAME_STATE_RUNNING) {
        return;
    }

    if (current != 0u) {
        inst = d_struct_get(w, current);
    }
    if (!inst) {
        u32 count = d_struct_count(w);
        double best_dist2 = 0.0;
        u32 i;
        for (i = 0u; i < count; ++i) {
            const d_struct_instance *cand = d_struct_get_by_index(w, i);
            if (!cand) {
                continue;
            }
            double dx = d_q16_16_to_double(cand->pos_x) - (double)m_camera.cx;
            double dy = d_q16_16_to_double(cand->pos_y) - (double)m_camera.cy;
            double dist2 = dx * dx + dy * dy;
            if (!inst || dist2 < best_dist2) {
                inst = cand;
                best_dist2 = dist2;
            }
        }
        if (inst) {
            m_last_struct_id = inst->id;
        }
    }

    std::snprintf(m_hud_instance_text, sizeof(m_hud_instance_text),
                  "Instance: %s / Seed: %u",
                  m_instance.id.c_str(),
                  (unsigned)m_instance.world_seed);

    std::snprintf(m_hud_remaining_text, sizeof(m_hud_remaining_text),
                  "Remaining: (n/a)");
    std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                  "Inventory: (empty)");

    if (inst) {
        dres_sample samples[4];
        u16 sample_count = 4u;
        q16_16 best = 0;
        q32_32 sx = ((q32_32)inst->pos_x) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
        q32_32 sy = ((q32_32)inst->pos_y) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
        q32_32 sz = ((q32_32)inst->pos_z) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);

        if (dres_sample_at(w, sx, sy, sz, 0u, samples, &sample_count) == 0 && sample_count > 0u) {
            u16 i;
            for (i = 0u; i < sample_count; ++i) {
                if (i == 0u || samples[i].value[0] > best) {
                    best = samples[i].value[0];
                }
            }
            std::snprintf(m_hud_remaining_text, sizeof(m_hud_remaining_text),
                          "Remaining v0: %d", d_q16_16_to_int(best));
        }

        {
            d_item_id item_id = 0u;
            u32 item_count = 0u;
            const d_proto_item *item_proto = (const d_proto_item *)0;
            if (d_struct_get_inventory_summary(w, inst->id, &item_id, &item_count) == 0 && item_id != 0u && item_count > 0u) {
                item_proto = d_content_get_item(item_id);
            }
            if (item_proto && item_proto->name) {
                std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                              "Inventory: %s x %u", item_proto->name, (unsigned)item_count);
            } else if (item_id != 0u && item_count > 0u) {
                std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                              "Inventory: #%u x %u", (unsigned)item_id, (unsigned)item_count);
            } else {
                std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                              "Inventory: (empty)");
            }
        }
    }

    {
        dui_widget *inst_label = dom_game_ui_get_instance_label();
        dui_widget *rem_label = dom_game_ui_get_remaining_label();
        dui_widget *inv_label = dom_game_ui_get_inventory_label();
        if (inst_label) inst_label->text = m_hud_instance_text;
        if (rem_label) rem_label->text = m_hud_remaining_text;
        if (inv_label) inv_label->text = m_hud_inventory_text;
    }
}

void DomGameApp::build_tool_select_extractor() {
    d_structure_proto_id id = dom_find_structure_by_name("Demo Extractor");
    if (id == 0u) {
        dom_game_ui_set_status(m_ui_ctx, "Tool: missing structure: Demo Extractor");
        return;
    }
    m_build_tool.set_place_structure(id);
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
}

void DomGameApp::build_tool_select_refiner() {
    d_structure_proto_id id = dom_find_structure_by_name("Demo Refiner");
    if (id == 0u) {
        dom_game_ui_set_status(m_ui_ctx, "Tool: missing structure: Demo Refiner");
        return;
    }
    m_build_tool.set_place_structure(id);
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
}

void DomGameApp::build_tool_select_assembler() {
    d_structure_proto_id id = dom_find_structure_by_name("Demo Assembler");
    if (id == 0u) {
        dom_game_ui_set_status(m_ui_ctx, "Tool: missing structure: Demo Assembler");
        return;
    }
    m_build_tool.set_place_structure(id);
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
}

void DomGameApp::build_tool_select_bin() {
    d_structure_proto_id id = dom_find_structure_by_name("Demo Bin");
    if (id == 0u) {
        dom_game_ui_set_status(m_ui_ctx, "Tool: missing structure: Demo Bin");
        return;
    }
    m_build_tool.set_place_structure(id);
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
}

void DomGameApp::build_tool_select_source() {
    build_tool_select_extractor();
}

void DomGameApp::build_tool_select_sink() {
    build_tool_select_bin();
}

void DomGameApp::build_tool_select_spline() {
    d_spline_profile_id id = dom_find_spline_profile_by_name("Demo Item Conveyor");
    if (id == 0u) {
        dom_game_ui_set_status(m_ui_ctx, "Tool: missing spline profile: Demo Item Conveyor");
        return;
    }
    m_build_tool.set_draw_spline(id);
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
}

void DomGameApp::build_tool_cancel() {
    m_build_tool.set_none();
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
}

void DomGameApp::update_debug_panel() {
    d_world_hash h = 0u;
    if (!m_runtime) {
        return;
    }

    h = (d_world_hash)dom_game_runtime_get_hash(m_runtime);

    if (m_detmode == 3u) {
        if (m_last_hash != 0u && h != m_last_hash) {
            const u64 tick = dom_game_runtime_get_tick(m_runtime);
            std::fprintf(stderr, "DET FAIL: world hash mismatch at tick %llu\n",
                         (unsigned long long)tick);
            std::abort();
        }
        m_last_hash = h;
    } else if (m_detmode != 0u) {
        m_last_hash = h;
    }

    if (m_show_debug_panel) {
        dom_game_ui_debug_update(m_ui_ctx, *this, h);
    }
}

void DomGameApp::clear_debug_probe() {
    m_debug_probe_set = false;
    m_debug_probe_x = 0;
    m_debug_probe_y = 0;
    m_debug_probe_z = 0;
}

void DomGameApp::set_debug_probe(q32_32 x, q32_32 y, q32_32 z) {
    m_debug_probe_set = true;
    m_debug_probe_x = x;
    m_debug_probe_y = y;
    m_debug_probe_z = z;
}

void DomGameApp::debug_probe_world_coords(q32_32 *out_x, q32_32 *out_y, q32_32 *out_z) const {
    if (!out_x || !out_y || !out_z) {
        return;
    }
    if (m_debug_probe_set) {
        *out_x = m_debug_probe_x;
        *out_y = m_debug_probe_y;
        *out_z = m_debug_probe_z;
        return;
    }

    {
        GameCamera cam = camera();
        q16_16 x16 = d_q16_16_from_double((double)cam.cx);
        q16_16 y16 = d_q16_16_from_double((double)cam.cy);
        *out_x = ((q32_32)x16) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
        *out_y = ((q32_32)y16) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
        *out_z = 0;
    }
}

void DomGameApp::toggle_overlay_hydrology() {
    if (!m_show_overlay_hydro) {
        m_show_overlay_hydro = true;
        m_show_overlay_temp = false;
        m_show_overlay_pressure = false;
    } else {
        m_show_overlay_hydro = false;
    }
}

void DomGameApp::toggle_overlay_temperature() {
    if (!m_show_overlay_temp) {
        m_show_overlay_temp = true;
        m_show_overlay_hydro = false;
        m_show_overlay_pressure = false;
    } else {
        m_show_overlay_temp = false;
    }
}

void DomGameApp::toggle_overlay_pressure() {
    if (!m_show_overlay_pressure) {
        m_show_overlay_pressure = true;
        m_show_overlay_hydro = false;
        m_show_overlay_temp = false;
    } else {
        m_show_overlay_pressure = false;
    }
}

void DomGameApp::toggle_overlay_volumes() {
    m_show_overlay_volumes = !m_show_overlay_volumes;
}

} // namespace dom
