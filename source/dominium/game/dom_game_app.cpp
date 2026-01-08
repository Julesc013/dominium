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

#include "dom_game_ui.h"
#include "dom_game_ui_debug.h"
#include "dom_game_save.h"
#include "runtime/dom_game_save.h"
#include "runtime/dom_game_replay.h"
#include "runtime/dom_game_content_id.h"
#include "runtime/dom_game_handshake.h"
#include "runtime/dom_derived_jobs.h"
#include "runtime/dom_snapshot.h"
#include "runtime/dom_io_guard.h"
#include "dom_game_tools_build.h"
#include "dominium/version.h"
#include "dominium/core_tlv.h"
#include "dominium/paths.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/gfx.h"
#include "domino/sys.h"
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
#include "net/d_net_cmd.h"
#include "net/d_net_proto.h"
#include "net/d_net_transport.h"
}

struct DomNetReplayRecorder {
    dom_game_replay_record *record;
};

extern "C" void dom_net_replay_tick_observer(
    void            *user,
    struct d_world  *w,
    u32              tick,
    const d_net_cmd *cmds,
    u32              cmd_count
) {
    DomNetReplayRecorder *rec = (DomNetReplayRecorder *)user;
    u32 i;
    (void)w;

    if (!rec || !rec->record) {
        return;
    }
    if (!cmds || cmd_count == 0u) {
        return;
    }

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
            return;
        }

        (void)dom_game_replay_record_write_cmd(rec->record, (u64)tick, buf, out_size);
        std::free(buf);
        buf = (unsigned char *)0;
    }
}

namespace dom {

namespace {

static const unsigned DEFAULT_TICK_RATE = 60u;
static const unsigned HEADLESS_SPLASH_MIN_MS = 50u;
static const unsigned HEADLESS_TIMEOUT_MS = 10000u;
static const u32 DEFAULT_DERIVED_BUDGET_MS = 2u;
static const u32 DEFAULT_DERIVED_BUDGET_IO_BYTES = 256u * 1024u;
static const u32 DEFAULT_DERIVED_BUDGET_JOBS = 4u;

static unsigned make_version_u32(unsigned major, unsigned minor, unsigned patch) {
    return major * 10000u + minor * 100u + patch;
}

static unsigned suite_version_u32() {
    return make_version_u32(DOMINIUM_VERSION_MAJOR,
                            DOMINIUM_VERSION_MINOR,
                            DOMINIUM_VERSION_PATCH);
}

enum {
    DOM_GAME_REFUSAL_TLV_VERSION = 1u,
    DOM_GAME_REFUSAL_TLV_TAG_CODE = 2u,
    DOM_GAME_REFUSAL_TLV_TAG_DETAIL = 3u,
    DOM_GAME_REFUSAL_TLV_TAG_RUN_ID = 4u,
    DOM_GAME_REFUSAL_TLV_TAG_INSTANCE_ID = 5u
};

enum {
    DOM_GAME_REFUSAL_HANDSHAKE_MISSING = 2001u,
    DOM_GAME_REFUSAL_HANDSHAKE_INVALID = 2002u,
    DOM_GAME_REFUSAL_HANDSHAKE_INSTANCE_MISMATCH = 2003u,
    DOM_GAME_REFUSAL_INSTANCE_ROOT_UNAVAILABLE = 2004u,
    DOM_GAME_REFUSAL_HANDSHAKE_SIM_CAPS_MISMATCH = 2005u,
    DOM_GAME_REFUSAL_UNIVERSE_OP_UNSUPPORTED = 2101u
};

static const char *path_refusal_detail(u32 code) {
    switch (code) {
    case DOM_GAME_PATHS_REFUSAL_MISSING_RUN_ROOT:
        return "missing_run_root";
    case DOM_GAME_PATHS_REFUSAL_MISSING_HOME_ROOT:
        return "missing_home_root";
    case DOM_GAME_PATHS_REFUSAL_INVALID_RUN_ROOT:
        return "invalid_run_root";
    case DOM_GAME_PATHS_REFUSAL_INVALID_HOME_ROOT:
        return "invalid_home_root";
    case DOM_GAME_PATHS_REFUSAL_ABSOLUTE_PATH:
        return "absolute_path_rejected";
    case DOM_GAME_PATHS_REFUSAL_TRAVERSAL:
        return "path_traversal_rejected";
    case DOM_GAME_PATHS_REFUSAL_NORMALIZATION:
        return "path_normalization_failed";
    case DOM_GAME_PATHS_REFUSAL_NON_CANONICAL:
        return "path_non_canonical";
    case DOM_GAME_PATHS_REFUSAL_OUTSIDE_ROOT:
        return "path_outside_root";
    default:
        return "path_refusal";
    }
}

static bool is_abs_path_input(const std::string &path) {
    if (path.empty()) {
        return false;
    }
    if (path[0] == '/' || path[0] == '\\') {
        return true;
    }
    if (path.size() >= 2u) {
        char c0 = path[0];
        if (((c0 >= 'A' && c0 <= 'Z') || (c0 >= 'a' && c0 <= 'z')) && path[1] == ':') {
            return true;
        }
    }
    return false;
}

static bool is_universe_action(DomGamePhaseAction action) {
    switch (action) {
    case DOM_GAME_PHASE_ACTION_NEW_UNIVERSE:
    case DOM_GAME_PHASE_ACTION_LOAD_UNIVERSE:
    case DOM_GAME_PHASE_ACTION_IMPORT_UNIVERSE:
    case DOM_GAME_PHASE_ACTION_EXPORT_UNIVERSE:
        return true;
    default:
        break;
    }
    return false;
}

static const char *universe_action_label(DomGamePhaseAction action) {
    switch (action) {
    case DOM_GAME_PHASE_ACTION_NEW_UNIVERSE:
        return "new";
    case DOM_GAME_PHASE_ACTION_LOAD_UNIVERSE:
        return "load";
    case DOM_GAME_PHASE_ACTION_IMPORT_UNIVERSE:
        return "import";
    case DOM_GAME_PHASE_ACTION_EXPORT_UNIVERSE:
        return "export";
    default:
        break;
    }
    return "unknown";
}

static DomSessionRole map_session_role(dom_game_session_role role) {
    switch (role) {
    case DOM_GAME_SESSION_ROLE_HOST:
        return DOM_SESSION_ROLE_HOST;
    case DOM_GAME_SESSION_ROLE_DEDICATED_SERVER:
        return DOM_SESSION_ROLE_DEDICATED_SERVER;
    case DOM_GAME_SESSION_ROLE_CLIENT:
        return DOM_SESSION_ROLE_CLIENT;
    case DOM_GAME_SESSION_ROLE_SINGLE:
    default:
        break;
    }
    return DOM_SESSION_ROLE_SINGLE;
}

static DomSessionAuthority map_session_authority(dom_game_session_authority auth) {
    switch (auth) {
    case DOM_GAME_SESSION_AUTH_LOCKSTEP:
        return DOM_SESSION_AUTH_LOCKSTEP;
    case DOM_GAME_SESSION_AUTH_SERVER:
    default:
        break;
    }
    return DOM_SESSION_AUTH_SERVER_AUTH;
}

static bool write_refusal_tlv(const DomGamePaths &paths,
                              u64 run_id,
                              const std::string &instance_id,
                              u32 code,
                              const std::string &detail) {
    if (paths.run_root.empty()) {
        return false;
    }

    core_tlv::TlvWriter w;
    w.add_u32(core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_GAME_REFUSAL_TLV_VERSION);
    w.add_u32(DOM_GAME_REFUSAL_TLV_TAG_CODE, code);
    if (run_id != 0ull) {
        w.add_u64(DOM_GAME_REFUSAL_TLV_TAG_RUN_ID, run_id);
    }
    if (!instance_id.empty()) {
        w.add_string(DOM_GAME_REFUSAL_TLV_TAG_INSTANCE_ID, instance_id);
    }
    if (!detail.empty()) {
        w.add_string(DOM_GAME_REFUSAL_TLV_TAG_DETAIL, detail);
    }

    {
        const std::string path = join(paths.run_root, "refusal.tlv");
        const std::vector<unsigned char> &bytes = w.bytes();
        if (!dom_io_guard_io_allowed()) {
            dom_io_guard_note_violation("refusal_write", path.c_str());
            return false;
        }
        void *fh = dsys_file_open(path.c_str(), "wb");
        size_t wrote = 0u;
        if (!fh) {
            return false;
        }
        if (!bytes.empty()) {
            wrote = dsys_file_write(fh, &bytes[0], bytes.size());
        }
        dsys_file_close(fh);
        return wrote == bytes.size();
    }
}

static void emit_refusal(const DomGamePaths &paths,
                         u64 run_id,
                         const std::string &instance_id,
                         u32 code,
                         const std::string &detail) {
    const bool wrote = write_refusal_tlv(paths, run_id, instance_id, code, detail);
    if (!wrote) {
        if (!detail.empty()) {
            std::fprintf(stderr, "DomGameApp refusal %u: %s\n", (unsigned)code, detail.c_str());
        } else {
            std::fprintf(stderr, "DomGameApp refusal %u\n", (unsigned)code);
        }
    }
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
      m_phase(),
      m_phase_action(DOM_GAME_PHASE_ACTION_NONE),
      m_universe_pending_action(DOM_GAME_PHASE_ACTION_NONE),
      m_bootstrap_started(false),
      m_bootstrap_failed(false),
      m_session_start_attempted(false),
      m_session_start_ok(false),
      m_session_start_failed(false),
      m_session_start_error(),
      m_running(false),
      m_mouse_x(0),
      m_mouse_y(0),
      m_last_struct_id(0),
      m_player_org_id(0u),
      m_dev_mode(false),
      m_detmode(0u),
      m_last_hash(0u),
      m_replay_last_tick(0u),
      m_replay_record(0),
      m_replay_play(0),
      m_net_replay_user(0),
      m_net_driver(0),
      m_runtime(0),
      m_session_role(DOM_SESSION_ROLE_SINGLE),
      m_session_authority(DOM_SESSION_AUTH_SERVER_AUTH),
      m_last_net_snapshot(),
      m_has_net_snapshot(false),
      m_derived_queue(0),
      m_last_wall_us(0u),
      m_derived_budget_ms(0u),
      m_derived_budget_io_bytes(0u),
      m_derived_budget_jobs(0u),
      m_show_debug_panel(false),
      m_ui_transparent_loading(false),
      m_debug_probe_set(false),
      m_debug_probe_x(0),
      m_debug_probe_y(0),
      m_debug_probe_z(0),
      m_show_overlay_hydro(false),
      m_show_overlay_temp(false),
      m_show_overlay_pressure(false),
      m_show_overlay_volumes(false),
      m_launcher_mode(false),
      m_dev_allow_ad_hoc_paths(false),
      m_allow_missing_content(false),
      m_headless_local(false),
      m_headless_reached_session(false),
      m_headless_abort_on_error(false),
      m_headless_tick_limit(0u),
      m_headless_ticks(0u),
      m_headless_elapsed_ms(0u),
      m_headless_timeout_ms(0u),
      m_exit_code(0),
      m_run_id(0u),
      m_refusal_code(0u),
      m_refusal_detail(),
      m_instance_manifest_hash() {
    std::memset(&m_ui_ctx, 0, sizeof(m_ui_ctx));
    std::memset(m_hud_instance_text, 0, sizeof(m_hud_instance_text));
    std::memset(m_hud_remaining_text, 0, sizeof(m_hud_remaining_text));
    std::memset(m_hud_inventory_text, 0, sizeof(m_hud_inventory_text));
    std::memset(m_menu_player_text, 0, sizeof(m_menu_player_text));
    std::memset(m_menu_server_text, 0, sizeof(m_menu_server_text));
    std::memset(m_menu_error_text, 0, sizeof(m_menu_error_text));
    std::memset(&m_cfg, 0, sizeof(m_cfg));
    std::memset(&m_fidelity, 0, sizeof(m_fidelity));
    std::memset(&m_last_net_snapshot, 0, sizeof(m_last_net_snapshot));
}

DomGameApp::~DomGameApp() {
    shutdown();
}

bool DomGameApp::init_from_cli(const dom_game_config &cfg) {
    shutdown();
    dom_io_guard_reset();

    m_cfg = cfg;
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
    m_save_path = cfg.save_path;
    m_load_path = cfg.load_path;
    m_universe_import_path = cfg.universe_import_path;
    m_universe_export_path = cfg.universe_export_path;
    m_universe_pending_action = DOM_GAME_PHASE_ACTION_NONE;
    if (!m_universe_import_path.empty()) {
        m_universe_pending_action = DOM_GAME_PHASE_ACTION_IMPORT_UNIVERSE;
    } else if (!m_universe_export_path.empty()) {
        m_universe_pending_action = DOM_GAME_PHASE_ACTION_EXPORT_UNIVERSE;
    }
    m_launcher_mode = (cfg.handshake_path[0] != '\0');
    m_dev_allow_ad_hoc_paths = (cfg.dev_allow_ad_hoc_paths != 0u);
    m_allow_missing_content = (cfg.dev_allow_missing_content != 0u);
    m_ui_transparent_loading = (cfg.ui_transparent_loading != 0u);
    m_headless_tick_limit = cfg.headless_ticks;
    m_headless_ticks = 0u;
    m_headless_elapsed_ms = 0u;
    m_headless_timeout_ms = (m_mode == GAME_MODE_HEADLESS && m_headless_tick_limit > 0u)
                                ? HEADLESS_TIMEOUT_MS
                                : 0u;
    m_headless_local = (cfg.headless_local != 0u);
    m_headless_reached_session = false;
    m_headless_abort_on_error = (m_mode == GAME_MODE_HEADLESS && m_headless_tick_limit > 0u);
    m_derived_budget_ms = cfg.derived_budget_ms ? cfg.derived_budget_ms : DEFAULT_DERIVED_BUDGET_MS;
    m_derived_budget_io_bytes = cfg.derived_budget_io_bytes ? cfg.derived_budget_io_bytes : DEFAULT_DERIVED_BUDGET_IO_BYTES;
    m_derived_budget_jobs = cfg.derived_budget_jobs ? cfg.derived_budget_jobs : DEFAULT_DERIVED_BUDGET_JOBS;
    m_exit_code = 0;
    m_run_id = 0u;
    m_refusal_code = 0u;
    m_refusal_detail.clear();
    m_instance_manifest_hash.clear();
    m_phase_action = DOM_GAME_PHASE_ACTION_NONE;
    m_bootstrap_started = false;
    m_bootstrap_failed = false;
    m_session_start_attempted = false;
    m_session_start_ok = false;
    m_session_start_failed = false;
    m_session_start_error.clear();
    dom_game_phase_init(m_phase);
    if (m_mode == GAME_MODE_HEADLESS) {
        m_phase.splash_min_ms = HEADLESS_SPLASH_MIN_MS;
    }
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
    if (!init_io_paths()) {
        std::printf("DomGameApp: failed to resolve run-scoped IO paths\n");
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
        const char *sys_backend = (cfg.platform_backend[0] == '\0')
                                      ? ((m_mode == GAME_MODE_HEADLESS) ? "null" : "win32")
                                      : cfg.platform_backend;
        std::printf("DomGameApp: initializing system backend '%s'\n", sys_backend);
        if (!d_system_init(sys_backend)) {
            std::printf("DomGameApp: system init failed\n");
            return false;
        }
    }

    {
        dom_derived_queue_desc qdesc;
        std::memset(&qdesc, 0, sizeof(qdesc));
        qdesc.struct_size = sizeof(qdesc);
        qdesc.struct_version = DOM_DERIVED_QUEUE_DESC_VERSION;
        qdesc.flags = (m_mode == GAME_MODE_HEADLESS) ? DOM_DERIVED_QUEUE_FLAG_ALLOW_IO : 0u;
        m_derived_queue = dom_derived_queue_create(&qdesc);
        if (!m_derived_queue) {
            std::printf("DomGameApp: derived job queue init failed\n");
            return false;
        }
    }
    dom_fidelity_init(&m_fidelity, DOM_FIDELITY_HIGH);

    if (m_mode != GAME_MODE_HEADLESS) {
        const char *gfx_backend = (cfg.gfx_backend[0] == '\0') ? "soft" : cfg.gfx_backend;
        std::printf("DomGameApp: initializing gfx backend '%s'\n", gfx_backend);
        if (!d_gfx_init(gfx_backend)) {
            std::printf("DomGameApp: gfx init failed\n");
            return false;
        }
    }

    if (!init_views_and_ui(cfg)) {
        std::printf("DomGameApp: view/UI init failed\n");
        return false;
    }

    m_phase.auto_start_join = (!m_connect_addr.empty());
    m_phase.auto_start_host = false;
    if (cfg.auto_host != 0u) {
        m_phase.auto_start_host = true;
    }
    if (!m_phase.auto_start_join &&
        (m_server_mode != SERVER_OFF || m_mode == GAME_MODE_HEADLESS)) {
        m_phase.auto_start_host = true;
    }
    if (cfg.session_role_set != 0u) {
        if (cfg.session_role == DOM_GAME_SESSION_ROLE_CLIENT) {
            m_phase.auto_start_join = true;
            m_phase.auto_start_host = false;
        } else {
            m_phase.auto_start_join = false;
            m_phase.auto_start_host = true;
        }
    }
    if (m_universe_pending_action != DOM_GAME_PHASE_ACTION_NONE) {
        m_phase.auto_start_join = false;
        m_phase.auto_start_host = false;
    }
    m_phase.server_addr = m_connect_addr;
    m_phase.server_port = m_net_port;
    if (m_phase.server_addr.empty()) {
        m_phase.server_addr = "127.0.0.1";
    }
    if (!m_instance.id.empty()) {
        m_phase.player_name = m_instance.id;
    }

    m_phase.prev_phase = DOM_GAME_PHASE_BOOT;
    m_phase.phase = DOM_GAME_PHASE_SPLASH;
    m_phase.phase_time_ms = 0u;
    handle_phase_enter(DOM_GAME_PHASE_BOOT, DOM_GAME_PHASE_SPLASH);

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
    if (m_main_view_id != 0u) {
        d_view_destroy(m_main_view_id);
        m_main_view_id = 0u;
    }

    dui_shutdown_context(&m_ui_ctx);

    if (m_derived_queue) {
        dom_derived_queue_destroy(m_derived_queue);
        m_derived_queue = 0;
    }

    if (!m_save_path.empty() && m_runtime) {
        const int rc = dom_game_runtime_save(m_runtime, m_save_path.c_str());
        if (rc != DOM_GAME_SAVE_OK) {
            std::printf("DomGameApp: failed to write save '%s' (rc=%d)\n",
                        m_save_path.c_str(), rc);
        }
    }

    d_net_set_tick_cmds_observer((d_net_tick_cmds_observer_fn)0, (void *)0);
    if (m_net_replay_user) {
        delete (struct DomNetReplayRecorder *)m_net_replay_user;
        m_net_replay_user = 0;
    }
    if (m_replay_record) {
        dom_game_replay_record_close(m_replay_record);
        m_replay_record = 0;
    }
    if (m_replay_play) {
        dom_game_replay_play_close(m_replay_play);
        m_replay_play = 0;
    }
    m_replay_last_tick = 0u;

    if (m_net_driver) {
        m_net_driver->stop();
        dom_net_driver_destroy(m_net_driver);
        m_net_driver = 0;
    }

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

void DomGameApp::request_exit() {
    m_running = false;
}

void DomGameApp::request_phase_action(DomGamePhaseAction action) {
    if (action == DOM_GAME_PHASE_ACTION_NONE) {
        return;
    }
    m_phase_action = action;
}

bool DomGameApp::init_paths(const dom_game_config &cfg) {
    DomGameHandshake hs;
    std::string home = cfg.dominium_home;
    std::string instance_id = cfg.instance_id[0] ? cfg.instance_id : "demo";
    u32 flags = DOM_GAME_PATHS_FLAG_NONE;

    if (m_launcher_mode) {
        flags |= DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED;
    }
    if (m_dev_allow_ad_hoc_paths) {
        flags |= DOM_GAME_PATHS_FLAG_DEV_ALLOW_AD_HOC;
    }

    if (!dom_game_paths_init_from_env(m_fs_paths, instance_id, 0u, flags)) {
        const u32 code = dom_game_paths_last_refusal(m_fs_paths);
        m_refusal_code = code;
        m_refusal_detail = path_refusal_detail(code);
        emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
        return false;
    }

    if (m_launcher_mode) {
        std::string handshake_abs;
        const std::string handshake_rel = cfg.handshake_path;

        if (handshake_rel.empty()) {
            m_refusal_code = DOM_GAME_REFUSAL_HANDSHAKE_MISSING;
            m_refusal_detail = "missing_handshake_path";
            emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
            return false;
        }

        if (m_dev_allow_ad_hoc_paths && is_abs_path_input(handshake_rel)) {
            handshake_abs = handshake_rel;
        } else {
            if (!dom_game_paths_resolve_rel(m_fs_paths,
                                            DOM_GAME_PATH_BASE_RUN_ROOT,
                                            handshake_rel,
                                            handshake_abs)) {
                const u32 code = dom_game_paths_last_refusal(m_fs_paths);
                m_refusal_code = code;
                m_refusal_detail = path_refusal_detail(code);
                emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
                return false;
            }
        }

        if (!dom_game_handshake_from_file(handshake_abs, hs)) {
            m_refusal_code = DOM_GAME_REFUSAL_HANDSHAKE_INVALID;
            m_refusal_detail = "handshake_parse_failed";
            emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
            return false;
        }
        if (cfg.instance_id[0] != '\0' && hs.instance_id != cfg.instance_id) {
            m_refusal_code = DOM_GAME_REFUSAL_HANDSHAKE_INSTANCE_MISMATCH;
            m_refusal_detail = "handshake_instance_mismatch";
            emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
            return false;
        }
        {
            DomSimCaps required;
            dom_sim_caps_init_default(required);
            if (!dom_sim_caps_compatible(hs.sim_caps, required)) {
                m_refusal_code = DOM_GAME_REFUSAL_HANDSHAKE_SIM_CAPS_MISMATCH;
                m_refusal_detail = "handshake_sim_caps_mismatch";
                emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
                return false;
            }
        }

        instance_id = hs.instance_id;
        m_run_id = hs.run_id;
        m_instance_manifest_hash = hs.instance_manifest_hash_bytes;

        if (!dom_game_paths_init_from_env(m_fs_paths, instance_id, hs.run_id, flags)) {
            const u32 code = dom_game_paths_last_refusal(m_fs_paths);
            m_refusal_code = code;
            m_refusal_detail = path_refusal_detail(code);
            emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
            return false;
        }
        if (hs.instance_root_ref.has_value) {
            if (!dom_game_paths_set_instance_root_ref(m_fs_paths,
                                                      hs.instance_root_ref.base_kind,
                                                      hs.instance_root_ref.rel)) {
                const u32 code = dom_game_paths_last_refusal(m_fs_paths);
                m_refusal_code = code;
                m_refusal_detail = path_refusal_detail(code);
                emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
                return false;
            }
        }
    }

    if (!m_fs_paths.run_root.empty() && !dir_exists(m_fs_paths.run_root)) {
        m_refusal_code = DOM_GAME_PATHS_REFUSAL_INVALID_RUN_ROOT;
        m_refusal_detail = path_refusal_detail(m_refusal_code);
        emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
        return false;
    }
    if (!m_fs_paths.home_root.empty() && !dir_exists(m_fs_paths.home_root)) {
        m_refusal_code = DOM_GAME_PATHS_REFUSAL_INVALID_HOME_ROOT;
        m_refusal_detail = path_refusal_detail(m_refusal_code);
        emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
        return false;
    }

    if (m_launcher_mode) {
        if (m_fs_paths.home_root.empty()) {
            m_refusal_code = DOM_GAME_REFUSAL_INSTANCE_ROOT_UNAVAILABLE;
            m_refusal_detail = "missing_instance_root";
            emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
            return false;
        }
        home = m_fs_paths.home_root;
    } else {
        if (home.empty() && !m_fs_paths.home_root.empty()) {
            home = m_fs_paths.home_root;
        }
        if (home.empty()) {
            const char *env_home = std::getenv("DOMINIUM_HOME");
            if (env_home && env_home[0] != '\0') {
                home = env_home;
            }
        }
        if (home.empty() && m_dev_allow_ad_hoc_paths) {
            std::fprintf(stderr, "DomGameApp: dev allow ad-hoc paths enabled; scanning for DOMINIUM_HOME\n");
            home = find_dominium_home_from(".");
            if (home.empty()) {
                const char *install_root = dmn_get_install_root();
                if (install_root && install_root[0] != '\0') {
                    home = find_dominium_home_from(install_root);
                }
            }
        }
        if (home.empty() && m_dev_allow_ad_hoc_paths) {
            home = ".";
        }
        if (home.empty()) {
            m_refusal_code = DOM_GAME_PATHS_REFUSAL_MISSING_HOME_ROOT;
            m_refusal_detail = path_refusal_detail(m_refusal_code);
            emit_refusal(m_fs_paths, m_run_id, instance_id, m_refusal_code, m_refusal_detail);
            return false;
        }
    }

    return resolve_paths(m_paths, home);
}

bool DomGameApp::init_io_paths(void) {
    struct PathSpec {
        std::string *path;
        DomGamePathBaseKind base_kind;
        const char *label;
        bool allow_ad_hoc;
    };

    PathSpec specs[] = {
        { &m_save_path, DOM_GAME_PATH_BASE_SAVE_DIR, "save", true },
        { &m_load_path, DOM_GAME_PATH_BASE_SAVE_DIR, "load", true },
        { &m_replay_record_path, DOM_GAME_PATH_BASE_REPLAY_DIR, "replay_record", true },
        { &m_replay_play_path, DOM_GAME_PATH_BASE_REPLAY_DIR, "replay_play", true },
        { &m_universe_import_path, DOM_GAME_PATH_BASE_RUN_ROOT, "universe_import", false },
        { &m_universe_export_path, DOM_GAME_PATH_BASE_RUN_ROOT, "universe_export", false }
    };
    size_t i;

    for (i = 0u; i < sizeof(specs) / sizeof(specs[0]); ++i) {
        std::string &path = *specs[i].path;
        if (path.empty()) {
            continue;
        }

        if (m_dev_allow_ad_hoc_paths && specs[i].allow_ad_hoc) {
            if (is_abs_path_input(path)) {
                std::fprintf(stderr,
                             "DomGameApp: dev allow ad-hoc paths enabled; using absolute %s path '%s'\n",
                             specs[i].label,
                             path.c_str());
                continue;
            }
            if (m_fs_paths.run_root.empty()) {
                std::fprintf(stderr,
                             "DomGameApp: dev allow ad-hoc paths enabled; using %s path '%s' as-is\n",
                             specs[i].label,
                             path.c_str());
                continue;
            }
        }

        {
            std::string resolved;
            if (!dom_game_paths_resolve_rel(m_fs_paths, specs[i].base_kind, path, resolved)) {
                const u32 code = dom_game_paths_last_refusal(m_fs_paths);
                m_refusal_code = code;
                m_refusal_detail = std::string("path_") + specs[i].label + ":" + path_refusal_detail(code);
                emit_refusal(m_fs_paths,
                             m_run_id,
                             m_fs_paths.instance_id.empty() ? m_instance.id : m_fs_paths.instance_id,
                             m_refusal_code,
                             m_refusal_detail);
                return false;
            }
            path.swap(resolved);
        }
    }
    return true;
}

bool DomGameApp::load_instance(const dom_game_config &cfg) {
    if (!m_fs_paths.instance_id.empty()) {
        m_instance.id = m_fs_paths.instance_id;
    } else {
        m_instance.id = cfg.instance_id[0] ? cfg.instance_id : "demo";
    }

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
    scfg.allow_missing_content = m_allow_missing_content;
    if (!m_session.init(m_paths, m_instance, scfg)) {
        return false;
    }

    /* Reset any previous net replay hook. */
    d_net_set_tick_cmds_observer((d_net_tick_cmds_observer_fn)0, (void *)0);
    if (m_net_replay_user) {
        delete (struct DomNetReplayRecorder *)m_net_replay_user;
        m_net_replay_user = 0;
    }
    if (m_replay_record) {
        dom_game_replay_record_close(m_replay_record);
        m_replay_record = 0;
    }
    if (m_replay_play) {
        dom_game_replay_play_close(m_replay_play);
        m_replay_play = 0;
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
        dom_game_replay_desc rdesc;
        std::memset(&rdesc, 0, sizeof(rdesc));
        rdesc.struct_size = sizeof(rdesc);
        rdesc.struct_version = DOM_GAME_REPLAY_DESC_VERSION;
        m_replay_play = dom_game_replay_play_open(m_replay_play_path.c_str(), &rdesc);
        if (!m_replay_play) {
            if (rdesc.error_code == DOM_GAME_REPLAY_ERR_MIGRATION) {
                std::printf("DomGameApp: replay migration required (version=%u)\n",
                            (unsigned)rdesc.container_version);
            } else {
                std::printf("DomGameApp: failed to load replay '%s'\n", m_replay_play_path.c_str());
            }
            return false;
        }
        if (rdesc.ups == 0u || rdesc.ups != m_tick_rate_hz) {
            std::printf("DomGameApp: replay ups mismatch (file=%u runtime=%u)\n",
                        (unsigned)rdesc.ups, (unsigned)m_tick_rate_hz);
            dom_game_replay_play_close(m_replay_play);
            m_replay_play = 0;
            return false;
        }
        if (cfg.replay_strict_content &&
            !dom_game_content_match_tlv(&m_session, rdesc.content_tlv, rdesc.content_tlv_len)) {
            std::printf("DomGameApp: replay content identity mismatch\n");
            dom_game_replay_play_close(m_replay_play);
            m_replay_play = 0;
            return false;
        }
        {
            const u64 last_tick = dom_game_replay_play_last_tick(m_replay_play);
            if (last_tick > 0xffffffffull) {
                std::printf("DomGameApp: replay tick index out of range (%llu)\n",
                            (unsigned long long)last_tick);
                dom_game_replay_play_close(m_replay_play);
                m_replay_play = 0;
                return false;
            }
            m_replay_last_tick = (u32)last_tick;
        }
        (void)d_net_cmd_queue_init();
    } else if (!m_replay_record_path.empty()) {
        std::vector<unsigned char> content_tlv;
        u64 seed = (u64)m_instance.world_seed;
        const d_world *world = m_session.world();
        if (world) {
            seed = (u64)world->meta.seed;
        }
        (void)dom_game_content_build_tlv(&m_session, content_tlv);
        m_replay_record = dom_game_replay_record_open(m_replay_record_path.c_str(),
                                                      m_tick_rate_hz,
                                                      seed,
                                                      m_instance.id.c_str(),
                                                      m_run_id,
                                                      m_instance_manifest_hash.empty() ? (const unsigned char *)0
                                                                                       : &m_instance_manifest_hash[0],
                                                      (u32)m_instance_manifest_hash.size(),
                                                      content_tlv.empty() ? (const unsigned char *)0 : &content_tlv[0],
                                                      (u32)content_tlv.size());
        if (!m_replay_record) {
            std::printf("DomGameApp: failed to init replay record\n");
            return false;
        }
        {
            struct DomNetReplayRecorder *rec = new DomNetReplayRecorder();
            rec->record = m_replay_record;
            m_net_replay_user = rec;
            d_net_set_tick_cmds_observer(dom_net_replay_tick_observer, rec);
        }
    }

    if (!m_net.init_single(m_tick_rate_hz)) {
        return false;
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
        rdesc.run_id = m_run_id;
        rdesc.instance_manifest_hash_bytes = m_instance_manifest_hash.empty() ? (const unsigned char *)0
                                                                               : &m_instance_manifest_hash[0];
        rdesc.instance_manifest_hash_len = (u32)m_instance_manifest_hash.size();

        m_runtime = dom_game_runtime_create(&rdesc);
        if (!m_runtime) {
            return false;
        }
        if (m_replay_play) {
            (void)dom_game_runtime_set_replay_playback(m_runtime, m_replay_play);
        }
        if (m_replay_last_tick > 0u) {
            (void)dom_game_runtime_set_replay_last_tick(m_runtime, m_replay_last_tick);
        }
        m_last_wall_us = 0u;
        if (!m_load_path.empty()) {
            const int rc = dom_game_runtime_load_save(m_runtime, m_load_path.c_str());
            if (rc != DOM_GAME_SAVE_OK) {
                std::printf("DomGameApp: failed to load save '%s' (rc=%d)\n",
                            m_load_path.c_str(), rc);
                return false;
            }
        }
    }

    ensure_demo_agents();
    return true;
}

bool DomGameApp::start_session(DomGamePhaseAction action, std::string &out_error) {
    out_error.clear();
    if (!m_session.is_initialized() || !m_runtime) {
        out_error = "runtime_not_ready";
        return false;
    }
    if (m_replay_play) {
        out_error = "replay_active";
        return false;
    }

    if (m_net_driver) {
        m_net_driver->stop();
        dom_net_driver_destroy(m_net_driver);
        m_net_driver = 0;
    }

    DomSessionConfig scfg;
    scfg.tick_rate_hz = m_tick_rate_hz;
    scfg.net_port = (m_phase.server_port != 0u) ? m_phase.server_port : m_net_port;
    if (m_cfg.session_input_delay != 0u) {
        scfg.input_delay_ticks = m_cfg.session_input_delay;
    }
    scfg.identity.instance_id = m_instance.id;
    scfg.identity.run_id = m_run_id;
    scfg.identity.instance_manifest_hash = m_instance_manifest_hash;
    scfg.identity.content_hash_bytes = m_instance_manifest_hash;
    if (m_cfg.session_authority_set != 0u) {
        scfg.authority = map_session_authority(m_cfg.session_authority);
    }
    scfg.flags = DOM_SESSION_FLAG_ENABLE_COMMANDS;
    if (m_mode != GAME_MODE_HEADLESS) {
        scfg.flags |= DOM_SESSION_FLAG_REQUIRE_UI;
    }
    if (scfg.authority == DOM_SESSION_AUTH_LOCKSTEP) {
        scfg.flags |= DOM_SESSION_FLAG_ENABLE_HASH_EXCHANGE;
    }

    {
        DomSessionRole role = DOM_SESSION_ROLE_SINGLE;
        const bool role_locked = (m_cfg.session_role_set != 0u);
        if (role_locked) {
            role = map_session_role(m_cfg.session_role);
        } else if (action == DOM_GAME_PHASE_ACTION_START_JOIN) {
            role = DOM_SESSION_ROLE_CLIENT;
        } else if (action == DOM_GAME_PHASE_ACTION_START_HOST) {
            if (m_headless_local) {
                role = DOM_SESSION_ROLE_SINGLE;
            } else if (m_server_mode == SERVER_DEDICATED) {
                role = DOM_SESSION_ROLE_DEDICATED_SERVER;
            } else {
                role = DOM_SESSION_ROLE_HOST;
            }
        } else {
            out_error = "invalid_session_action";
            return false;
        }

        if (role_locked) {
            if (action == DOM_GAME_PHASE_ACTION_START_JOIN &&
                role != DOM_SESSION_ROLE_CLIENT) {
                out_error = "role_action_mismatch";
                return false;
            }
            if (action == DOM_GAME_PHASE_ACTION_START_HOST &&
                role == DOM_SESSION_ROLE_CLIENT) {
                out_error = "role_action_mismatch";
                return false;
            }
        }

        scfg.role = role;
    }

    if (scfg.role == DOM_SESSION_ROLE_CLIENT) {
        std::string addr = m_phase.server_addr.empty() ? m_connect_addr : m_phase.server_addr;
        if (addr.empty()) {
            out_error = "missing_server_addr";
            return false;
        }
        scfg.connect_addr = addr;
        if (scfg.net_port == 0u) {
            scfg.net_port = m_net_port;
        }
    } else {
        scfg.connect_addr.clear();
    }

    {
        u32 refusal = 0u;
        std::string detail;
        if (!dom_session_config_validate(scfg, &refusal, &detail)) {
            (void)refusal;
            out_error = detail.empty() ? "invalid_session_config" : detail;
            return false;
        }
    }

    m_session_role = scfg.role;
    m_session_authority = scfg.authority;
    m_has_net_snapshot = false;
    std::memset(&m_last_net_snapshot, 0, sizeof(m_last_net_snapshot));

    {
        DomNetDriverContext ctx;
        ctx.net = &m_net;
        ctx.runtime = m_runtime;
        ctx.instance = &m_instance;
        ctx.paths = &m_fs_paths;
        m_net_driver = dom_net_driver_create(scfg, ctx, &out_error);
        if (!m_net_driver) {
            if (out_error.empty()) {
                out_error = "net_driver_create_failed";
            }
            return false;
        }
        if (m_net_driver->start() != DOM_NET_DRIVER_OK) {
            m_net_driver->stop();
            dom_net_driver_destroy(m_net_driver);
            m_net_driver = 0;
            if (out_error.empty()) {
                out_error = "net_driver_start_failed";
            }
            return false;
        }
    }

    return true;
}

void DomGameApp::handle_phase_enter(DomGamePhaseId prev_phase, DomGamePhaseId next_phase) {
    if (next_phase == DOM_GAME_PHASE_SPLASH) {
        dom_game_ui_build_splash(m_ui_ctx);
        if (!m_bootstrap_started) {
            m_bootstrap_started = true;
            if (!init_session(m_cfg)) {
                m_bootstrap_failed = true;
                m_session_start_error = "bootstrap_failed";
                request_phase_action(DOM_GAME_PHASE_ACTION_QUIT_APP);
            }
        }
        return;
    }
    if (next_phase == DOM_GAME_PHASE_MAIN_MENU) {
        if (prev_phase == DOM_GAME_PHASE_SESSION_LOADING ||
            prev_phase == DOM_GAME_PHASE_IN_SESSION) {
            if (m_net_driver) {
                m_net_driver->stop();
                dom_net_driver_destroy(m_net_driver);
                m_net_driver = 0;
            }
            m_net.shutdown();
            if (!init_session(m_cfg)) {
                std::fprintf(stderr, "DomGameApp: session reset failed\n");
                m_phase.has_error = true;
                m_phase.last_error = "session_reset_failed";
            }
        }
        dom_game_ui_build_main_menu(m_ui_ctx);
        update_menu_labels();
        if (m_universe_pending_action != DOM_GAME_PHASE_ACTION_NONE) {
            handle_universe_action(m_universe_pending_action);
            m_universe_pending_action = DOM_GAME_PHASE_ACTION_NONE;
        }
        return;
    }
    if (next_phase == DOM_GAME_PHASE_SESSION_START) {
        std::string err;
        dom_game_ui_build_session_loading(m_ui_ctx);
        if (!start_session(m_phase.session_action, err)) {
            std::fprintf(stderr, "DomGameApp: session start failed (%s)\n", err.c_str());
            m_session_start_failed = true;
            m_session_start_error = err;
            if (m_mode == GAME_MODE_HEADLESS && m_headless_abort_on_error) {
                m_exit_code = 1;
                request_exit();
            }
        } else {
            m_session_start_ok = true;
        }
        return;
    }
    if (next_phase == DOM_GAME_PHASE_SESSION_LOADING) {
        dom_game_ui_build_session_loading(m_ui_ctx);
        return;
    }
    if (next_phase == DOM_GAME_PHASE_IN_SESSION) {
        if (m_mode == GAME_MODE_HEADLESS) {
            m_headless_reached_session = true;
        }
        dom_game_ui_build_in_game(m_ui_ctx);
        return;
    }
    if (next_phase == DOM_GAME_PHASE_SHUTDOWN) {
        request_exit();
        return;
    }
}

void DomGameApp::update_phase(u32 dt_ms) {
    DomGamePhaseInput in;
    const DomGamePhaseAction action = m_phase_action;
    std::memset(&in, 0, sizeof(in));
    in.dt_ms = dt_ms;
    in.action = action;
    in.runtime_ready = (m_runtime != 0);
    in.content_ready = m_session.is_initialized();
    in.net_ready = m_net_driver ? m_net_driver->ready() : false;
    in.world_ready = m_session.is_initialized();
    in.world_progress = m_session.is_initialized() ? 100u : 0u;
    in.session_start_ok = m_session_start_ok;
    in.session_start_failed = m_session_start_failed;
    in.session_error = m_session_start_failed ? m_session_start_error.c_str() : (const char *)0;

    m_phase_action = DOM_GAME_PHASE_ACTION_NONE;
    m_session_start_ok = false;
    m_session_start_failed = false;
    m_session_start_error.clear();

    if (dom_game_phase_update(m_phase, in)) {
        std::printf("DomGameApp: phase %s -> %s\n",
                    dom_game_phase_name(m_phase.prev_phase),
                    dom_game_phase_name(m_phase.phase));
        handle_phase_enter(m_phase.prev_phase, m_phase.phase);
    }
    if (m_phase.phase == DOM_GAME_PHASE_MAIN_MENU && is_universe_action(action)) {
        handle_universe_action(action);
    }
    dom_game_phase_render(m_phase, m_ui_ctx, dt_ms);
}

void DomGameApp::update_menu_labels() {
    const char *player = m_phase.player_name.empty() ? "Player" : m_phase.player_name.c_str();
    std::snprintf(m_menu_player_text, sizeof(m_menu_player_text), "Player: %s", player);

    if (!m_phase.server_addr.empty()) {
        if (m_phase.server_port != 0u) {
            std::snprintf(m_menu_server_text,
                          sizeof(m_menu_server_text),
                          "Server: %s:%u",
                          m_phase.server_addr.c_str(),
                          (unsigned)m_phase.server_port);
        } else {
            std::snprintf(m_menu_server_text,
                          sizeof(m_menu_server_text),
                          "Server: %s",
                          m_phase.server_addr.c_str());
        }
    } else {
        std::snprintf(m_menu_server_text, sizeof(m_menu_server_text), "Server: (unset)");
    }

    if (m_phase.has_error && !m_phase.last_error.empty()) {
        std::snprintf(m_menu_error_text,
                      sizeof(m_menu_error_text),
                      "Error: %s",
                      m_phase.last_error.c_str());
    } else {
        m_menu_error_text[0] = '\0';
    }

    dom_game_ui_set_menu_player(m_ui_ctx, m_menu_player_text);
    dom_game_ui_set_menu_server(m_ui_ctx, m_menu_server_text);
    dom_game_ui_set_menu_error(m_ui_ctx, m_menu_error_text);
}

void DomGameApp::handle_universe_action(DomGamePhaseAction action) {
    if (!is_universe_action(action)) {
        return;
    }
    const char *label = universe_action_label(action);
    std::string detail = std::string("universe_") + label + "_not_implemented";

    m_phase.has_error = true;
    m_phase.last_error = detail;
    update_menu_labels();

    m_refusal_code = DOM_GAME_REFUSAL_UNIVERSE_OP_UNSUPPORTED;
    m_refusal_detail = detail;
    emit_refusal(m_fs_paths,
                 m_run_id,
                 m_fs_paths.instance_id.empty() ? m_instance.id : m_fs_paths.instance_id,
                 m_refusal_code,
                 m_refusal_detail);

    std::fprintf(stderr, "DomGameApp: universe %s not implemented\n", label);
}

bool DomGameApp::init_views_and_ui(const dom_game_config &cfg) {
    d_view_desc desc;

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

    if (m_mode != GAME_MODE_HEADLESS) {
        m_main_view_id = d_view_create(&desc);
        if (m_main_view_id == 0u) {
            return false;
        }
    } else {
        m_main_view_id = 0u;
    }

    dui_shutdown_context(&m_ui_ctx);
    dui_init_context(&m_ui_ctx);
    dom_game_ui_set_app(this);

    dom_game_ui_build_root(m_ui_ctx, m_mode);
    if (cfg.ui_transparent_loading && m_mode != GAME_MODE_HEADLESS) {
        std::fprintf(stderr,
                     "DomGameApp: transparent loading requested; using opaque fallback.\n");
    }
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
    const u32 stall_threshold_ms = 100u;

    while (m_running) {
        bool should_break = false;
        const u64 frame_start_us = dsys_time_now_us();

        dom_io_guard_enter_ui();

        if (d_system_pump_events() != 0) {
            m_running = false;
            should_break = true;
        }
        if (!should_break) {
            tick_fixed();
            if (!m_running) {
                should_break = true;
            }
        }
        if (!should_break && m_mode != GAME_MODE_HEADLESS) {
            render_frame();
        }
        dom_io_guard_exit_ui();

        {
            const u64 frame_end_us = dsys_time_now_us();
            const u64 frame_ms = (frame_end_us >= frame_start_us)
                                     ? ((frame_end_us - frame_start_us) / 1000ull)
                                     : 0ull;
            if (frame_ms > (u64)stall_threshold_ms) {
                dom_io_guard_note_stall((u32)frame_ms, stall_threshold_ms);
            }
        }

        if (should_break) {
            break;
        }
    }
}

void DomGameApp::tick_fixed() {
    const u64 now_us = dsys_time_now_us();
    const u64 dt_us = (m_last_wall_us > 0u && now_us >= m_last_wall_us) ? (now_us - m_last_wall_us) : 0u;
    m_last_wall_us = now_us;
    const bool server_auth_client = (m_session_role == DOM_SESSION_ROLE_CLIENT &&
                                     m_session_authority == DOM_SESSION_AUTH_SERVER_AUTH);

    if (m_mode != GAME_MODE_HEADLESS) {
        process_input_events();
        update_camera();
    }

    {
        bool derived_pending = false;
        bool surface_pending = false;
        if (m_derived_queue || m_runtime) {
            dom_io_guard_enter_derived();
            if (m_derived_queue) {
                (void)dom_derived_pump(m_derived_queue,
                                       m_derived_budget_ms,
                                       (u64)m_derived_budget_io_bytes,
                                       m_derived_budget_jobs);
            }
            if (m_runtime) {
                (void)dom_game_runtime_pump_surface_chunks(m_runtime,
                                                           m_derived_budget_ms,
                                                           (u64)m_derived_budget_io_bytes,
                                                           m_derived_budget_jobs);
                surface_pending = dom_game_runtime_surface_has_pending(m_runtime) != 0;
            }
            dom_io_guard_exit_derived();
        }
        if (m_derived_queue) {
            dom_derived_stats stats;
            if (dom_derived_stats(m_derived_queue, &stats) == 0) {
                if (stats.queued > 0u || stats.running > 0u) {
                    derived_pending = true;
                }
            }
        }
        if (derived_pending || surface_pending) {
            dom_fidelity_mark_missing(&m_fidelity, DOM_FIDELITY_MISSING_DERIVED);
        } else {
            dom_fidelity_mark_ready(&m_fidelity, DOM_FIDELITY_MISSING_DERIVED);
        }
        dom_fidelity_step(&m_fidelity);
    }

    if (m_session.is_initialized() && m_runtime &&
        (m_phase.phase == DOM_GAME_PHASE_SESSION_LOADING ||
         m_phase.phase == DOM_GAME_PHASE_IN_SESSION)) {
        if (m_net_driver) {
            (void)m_net_driver->pump_network();
            {
                dom_game_net_snapshot_desc desc;
                if (m_net_driver->get_last_snapshot(&desc) == DOM_NET_DRIVER_OK) {
                    m_last_net_snapshot = desc;
                    m_has_net_snapshot = true;
                }
            }
        } else {
            (void)dom_game_runtime_pump(m_runtime);
        }
    }

    u32 dt_ms = (u32)(dt_us / 1000ull);
    if (dt_ms == 0u && dt_us > 0u) {
        dt_ms = 1u;
    }
    update_phase(dt_ms);

    if (m_mode == GAME_MODE_HEADLESS && dt_ms > 0u) {
        m_headless_elapsed_ms += dt_ms;
    }
    if (m_mode == GAME_MODE_HEADLESS && m_headless_abort_on_error && m_phase.has_error) {
        m_exit_code = 1;
        request_exit();
        return;
    }
    if (m_mode == GAME_MODE_HEADLESS &&
        m_headless_timeout_ms > 0u &&
        !m_headless_reached_session &&
        m_headless_elapsed_ms >= m_headless_timeout_ms) {
        std::fprintf(stderr, "DomGameApp: headless timeout waiting for IN_SESSION\n");
        m_exit_code = 1;
        request_exit();
        return;
    }

    if (m_session.is_initialized() && m_phase.phase == DOM_GAME_PHASE_IN_SESSION && m_runtime) {
        if (!server_auth_client) {
            u32 stepped = 0u;
            const int rc = dom_game_runtime_tick_wall(m_runtime, dt_us, &stepped);
            if (rc == DOM_GAME_RUNTIME_REPLAY_END) {
                m_exit_code = 0;
                request_exit();
                return;
            }
            if (rc == DOM_GAME_RUNTIME_ERR) {
                m_exit_code = 1;
                request_exit();
                return;
            }
            if (m_mode == GAME_MODE_HEADLESS && m_headless_tick_limit > 0u) {
                m_headless_ticks += stepped;
                if (m_headless_ticks >= m_headless_tick_limit) {
                    std::printf("DomGameApp: headless tick limit reached (%u)\n",
                                (unsigned)m_headless_tick_limit);
                    request_exit();
                    return;
                }
            }
        }
    }
    dom_game_snapshot *snapshot = (dom_game_snapshot *)0;
    if (m_runtime) {
        snapshot = dom_game_runtime_build_snapshot(m_runtime, DOM_GAME_SNAPSHOT_FLAG_RUNTIME);
        if (snapshot) {
            snapshot->view.camera_x = m_camera.cx;
            snapshot->view.camera_y = m_camera.cy;
            snapshot->view.camera_zoom = m_camera.zoom;
            snapshot->view.selected_struct_id = (u32)m_last_struct_id;
            if (server_auth_client && m_has_net_snapshot) {
                snapshot->runtime.tick_index = m_last_net_snapshot.tick_index;
                snapshot->runtime.ups = m_last_net_snapshot.ups;
                snapshot->runtime.vessel_count = m_last_net_snapshot.vessel_count;
                snapshot->runtime.sim_hash = 0u;
            }
        }
    }
    update_demo_hud(snapshot);
    dom_game_ui_set_status(m_ui_ctx, m_build_tool.status_text());
    update_debug_panel(snapshot);
    dom_game_runtime_release_snapshot(snapshot);
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

    {
        d_world *w = world();
        const u32 fidelity = m_fidelity.level;
        if (w && fidelity >= DOM_FIDELITY_LOW) {
            d_view_render(w, view, &frame);
        }
        if (fidelity >= DOM_FIDELITY_MED) {
            dom_draw_debug_overlays(*this, w, cmd_buffer, width, height);
        }
        if (fidelity >= DOM_FIDELITY_HIGH) {
            dom_draw_trans_overlays(*this, w, cmd_buffer, width, height);
        }
    }
    m_build_tool.render_overlay(*this, cmd_buffer, width, height);
    dui_layout(&m_ui_ctx, &root_rect);
    dui_render(&m_ui_ctx, &frame);

    d_gfx_cmd_buffer_end(cmd_buffer);
    d_gfx_submit(cmd_buffer);
    d_gfx_present();
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
                if (m_phase.phase == DOM_GAME_PHASE_IN_SESSION ||
                    m_phase.phase == DOM_GAME_PHASE_SESSION_LOADING) {
                    request_phase_action(DOM_GAME_PHASE_ACTION_QUIT_TO_MENU);
                } else {
                    request_phase_action(DOM_GAME_PHASE_ACTION_QUIT_APP);
                }
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

void DomGameApp::update_demo_hud(const dom_game_snapshot *snapshot) {
    if (!snapshot || m_phase.phase != DOM_GAME_PHASE_IN_SESSION) {
        return;
    }

    std::snprintf(m_hud_instance_text, sizeof(m_hud_instance_text),
                  "Instance: %s / Seed: %u",
                  m_instance.id.c_str(),
                  (unsigned)m_instance.world_seed);

    std::snprintf(m_hud_remaining_text, sizeof(m_hud_remaining_text),
                  "Entities: %u", (unsigned)snapshot->runtime.entity_count);

    std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                  "Constructions: %u", (unsigned)snapshot->runtime.construction_count);

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

void DomGameApp::update_debug_panel(const dom_game_snapshot *snapshot) {
    d_world_hash h = 0u;
    u64 tick = 0ull;

    if (snapshot) {
        h = (d_world_hash)snapshot->runtime.sim_hash;
        tick = snapshot->runtime.tick_index;
    }

    if (m_detmode == 3u) {
        if (m_last_hash != 0u && h != m_last_hash) {
            std::fprintf(stderr, "DET FAIL: world hash mismatch at tick %llu\n",
                         (unsigned long long)tick);
            std::abort();
        }
        m_last_hash = h;
    } else if (m_detmode != 0u) {
        m_last_hash = h;
    }

    if (m_show_debug_panel) {
        dom_game_ui_debug_update(m_ui_ctx, *this, snapshot);
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
