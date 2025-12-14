#include "dom_game_tools_build.h"

#include <cstdio>
#include <cstring>
#include <vector>

#include "dom_game_app.h"
#include "dom_game_ui.h"

extern "C" {
#include "build/d_build.h"
#include "content/d_content.h"
#include "core/dg_quant.h"
#include "net/d_net_schema.h"
#include "trans/d_trans_spline.h"
}

namespace dom {

namespace {

static double dom_px_per_unit(double zoom) {
    double px;
    if (zoom < 1.0) {
        zoom = 1.0;
    }
    px = 32.0 * (50.0 / zoom);
    if (px < 2.0) px = 2.0;
    if (px > 96.0) px = 96.0;
    return px;
}

static void dom_screen_to_world_xy(
    const GameCamera &cam,
    int mouse_x,
    int mouse_y,
    q32_32 *out_x,
    q32_32 *out_y
) {
    i32 width = 800;
    i32 height = 600;
    double px_per_unit;
    double wx;
    double wy;
    q16_16 x16;
    q16_16 y16;

    d_gfx_get_surface_size(&width, &height);
    px_per_unit = dom_px_per_unit((double)cam.zoom);

    wx = (double)cam.cx + ((double)mouse_x - (double)width * 0.5) / px_per_unit;
    wy = (double)cam.cy + ((double)mouse_y - (double)height * 0.5) / px_per_unit;

    x16 = d_q16_16_from_double(wx);
    y16 = d_q16_16_from_double(wy);

    if (out_x) {
        *out_x = ((q32_32)x16) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
    }
    if (out_y) {
        *out_y = ((q32_32)y16) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
    }
}

static void dom_world_xy_to_screen(
    const GameCamera &cam,
    i32 width,
    i32 height,
    q32_32 wx,
    q32_32 wy,
    i32 *out_sx,
    i32 *out_sy
) {
    double px_per_unit = dom_px_per_unit((double)cam.zoom);
    q16_16 x16 = (q16_16)(wx >> (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS));
    q16_16 y16 = (q16_16)(wy >> (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS));
    double x = d_q16_16_to_double(x16);
    double y = d_q16_16_to_double(y16);
    double sx = (double)width * 0.5 + (x - (double)cam.cx) * px_per_unit;
    double sy = (double)height * 0.5 + (y - (double)cam.cy) * px_per_unit;
    if (out_sx) *out_sx = (i32)(sx + 0.5);
    if (out_sy) *out_sy = (i32)(sy + 0.5);
}

static void dom_emit_point(d_gfx_cmd_buffer *buf, i32 x, i32 y, i32 size, d_gfx_color c) {
    d_gfx_draw_rect_cmd r;
    if (!buf) return;
    if (size < 1) size = 1;
    r.x = x - size / 2;
    r.y = y - size / 2;
    r.w = size;
    r.h = size;
    r.color = c;
    d_gfx_cmd_draw_rect(buf, &r);
}

static void dom_emit_outline(d_gfx_cmd_buffer *buf, i32 x, i32 y, i32 w, i32 h, i32 thickness, d_gfx_color c) {
    d_gfx_draw_rect_cmd r;
    if (!buf) return;
    if (thickness < 1) thickness = 1;
    r.color = c;
    r.x = x; r.y = y; r.w = w; r.h = thickness; d_gfx_cmd_draw_rect(buf, &r);
    r.x = x; r.y = y + h - thickness; r.w = w; r.h = thickness; d_gfx_cmd_draw_rect(buf, &r);
    r.x = x; r.y = y; r.w = thickness; r.h = h; d_gfx_cmd_draw_rect(buf, &r);
    r.x = x + w - thickness; r.y = y; r.w = thickness; r.h = h; d_gfx_cmd_draw_rect(buf, &r);
}

static void dom_tlv_write_raw(std::vector<unsigned char> &out, u32 tag, const void *data, u32 len) {
    const size_t base = out.size();
    out.resize(base + 8u + (size_t)len);
    std::memcpy(&out[base], &tag, 4u);
    std::memcpy(&out[base + 4u], &len, 4u);
    if (len > 0u && data) {
        std::memcpy(&out[base + 8u], data, (size_t)len);
    }
}

static void dom_tlv_write_u32(std::vector<unsigned char> &out, u32 tag, u32 v) {
    dom_tlv_write_raw(out, tag, &v, 4u);
}

static void dom_tlv_write_i64(std::vector<unsigned char> &out, u32 tag, i64 v) {
    dom_tlv_write_raw(out, tag, &v, 8u);
}

static void dom_tlv_write_u64(std::vector<unsigned char> &out, u32 tag, u64 v) {
    dom_tlv_write_raw(out, tag, &v, 8u);
}

static void dom_tlv_write_q16_16(std::vector<unsigned char> &out, u32 tag, q16_16 v) {
    i32 tmp = (i32)v;
    dom_tlv_write_raw(out, tag, &tmp, 4u);
}

static u32 dom_next_cmd_tick(const DomGameApp &app, const d_world *w) {
    u32 now = (w) ? w->tick_count : 0u;
    u32 delay = app.net().input_delay_ticks();
    if (delay < 1u) {
        delay = 1u;
    }
    return now + delay;
}

} // namespace

DomGameBuildTool::DomGameBuildTool()
    : m_mode(MODE_NONE),
      m_structure_id(0u),
      m_spline_profile_id(0u),
      m_yaw(0),
      m_mouse_x(0),
      m_mouse_y(0),
      m_spline_active(0),
      m_spline_node_count(0u)
{
    m_status[0] = '\0';
    set_status("Tool: (none)");
    std::memset(m_spline_nodes, 0, sizeof(m_spline_nodes));
}

void DomGameBuildTool::set_status(const char *text) {
    if (!text) {
        m_status[0] = '\0';
        return;
    }
    std::snprintf(m_status, sizeof(m_status), "%s", text);
}

void DomGameBuildTool::clear_spline() {
    m_spline_active = 0;
    m_spline_node_count = 0u;
    std::memset(m_spline_nodes, 0, sizeof(m_spline_nodes));
}

void DomGameBuildTool::set_none() {
    m_mode = MODE_NONE;
    m_structure_id = 0u;
    m_spline_profile_id = 0u;
    clear_spline();
    set_status("Tool: (none)");
}

void DomGameBuildTool::set_place_structure(d_structure_proto_id structure_id) {
    const d_proto_structure *sp;
    m_mode = MODE_PLACE_STRUCTURE;
    m_structure_id = structure_id;
    clear_spline();

    sp = d_content_get_structure(structure_id);
    if (sp && sp->name) {
        std::snprintf(m_status, sizeof(m_status),
                      "Tool: Place Structure: %s (Q/E rotate, click to place)",
                      sp->name);
    } else if (structure_id != 0u) {
        std::snprintf(m_status, sizeof(m_status),
                      "Tool: Place Structure: #%u (Q/E rotate, click to place)",
                      (unsigned)structure_id);
    } else {
        set_status("Tool: Place Structure (invalid)");
    }
}

void DomGameBuildTool::set_draw_spline(d_spline_profile_id spline_profile_id) {
    const d_proto_spline_profile *pp;
    m_mode = MODE_DRAW_SPLINE;
    m_spline_profile_id = spline_profile_id;
    clear_spline();

    pp = d_content_get_spline_profile(spline_profile_id);
    if (pp && pp->name) {
        std::snprintf(m_status, sizeof(m_status),
                      "Tool: Draw Spline: %s (click to add nodes, right-click to finish)",
                      pp->name);
    } else if (spline_profile_id != 0u) {
        std::snprintf(m_status, sizeof(m_status),
                      "Tool: Draw Spline: #%u (click to add nodes, right-click to finish)",
                      (unsigned)spline_profile_id);
    } else {
        set_status("Tool: Draw Spline (invalid)");
    }
}

void DomGameBuildTool::set_mouse_pos(int x, int y) {
    m_mouse_x = x;
    m_mouse_y = y;
}

void DomGameBuildTool::rotate_step(int dir) {
    const q16_16 step = (q16_16)(1 << 14); /* 0.25 turns */
    q16_16 yaw = m_yaw;
    if (dir < 0) {
        yaw = (q16_16)(yaw - step);
    } else {
        yaw = (q16_16)(yaw + step);
    }
    if (yaw < 0) {
        yaw = (q16_16)(yaw + (q16_16)(1 << 16));
    } else if (yaw >= (q16_16)(1 << 16)) {
        yaw = (q16_16)(yaw - (q16_16)(1 << 16));
    }
    m_yaw = yaw;
}

int DomGameBuildTool::commit_place_structure(DomGameApp &app, q32_32 wx, q32_32 wy) {
    d_world *w = app.session().world();
    d_net_cmd cmd;
    std::vector<unsigned char> payload;
    u32 tick;

    if (!w || m_structure_id == 0u) {
        set_status("Build: no world or structure selected");
        return 0;
    }
    if (!app.net().ready()) {
        set_status("Build: session not ready");
        return 0;
    }

    payload.reserve(64u);
    dom_tlv_write_u32(payload, D_NET_TLV_BUILD2_KIND, (u32)D_BUILD_KIND_STRUCTURE);
    dom_tlv_write_u32(payload, D_NET_TLV_BUILD2_STRUCTURE_PROTO_ID, (u32)m_structure_id);
    dom_tlv_write_u32(payload, D_NET_TLV_BUILD2_OWNER_ORG_ID, (u32)app.player_org_id());
    dom_tlv_write_u32(payload, D_NET_TLV_BUILD2_FLAGS, 0u);

    /* Anchor+pose contract: use a terrain anchor in world frame (frame id 0). */
    dom_tlv_write_u32(payload, D_NET_TLV_BUILD2_ANCHOR_KIND, (u32)DG_ANCHOR_TERRAIN);
    dom_tlv_write_u64(payload, D_NET_TLV_BUILD2_HOST_FRAME, (u64)DG_FRAME_ID_WORLD);
    {
        dg_q u = (dg_q)((i64)wx >> (Q32_32_FRAC_BITS - 16));
        dg_q v = (dg_q)((i64)wy >> (Q32_32_FRAC_BITS - 16));
        u = dg_quant_param(u, DG_QUANT_PARAM_DEFAULT_Q);
        v = dg_quant_param(v, DG_QUANT_PARAM_DEFAULT_Q);
        dom_tlv_write_i64(payload, D_NET_TLV_BUILD2_TERRAIN_U, (i64)u);
        dom_tlv_write_i64(payload, D_NET_TLV_BUILD2_TERRAIN_V, (i64)v);
        dom_tlv_write_i64(payload, D_NET_TLV_BUILD2_TERRAIN_H, (i64)0);
    }

    tick = dom_next_cmd_tick(app, w);
    std::memset(&cmd, 0, sizeof(cmd));
    cmd.schema_id = (u32)D_NET_SCHEMA_CMD_BUILD_V2;
    cmd.schema_ver = 1u;
    cmd.tick = tick;
    cmd.payload.ptr = payload.empty() ? (unsigned char *)0 : &payload[0];
    cmd.payload.len = (u32)payload.size();

    if (!app.net().submit_cmd(&cmd)) {
        set_status("Build: send failed");
        return 0;
    }

    {
        const d_proto_structure *sp = d_content_get_structure(m_structure_id);
        if (sp && sp->name) {
            std::snprintf(m_status, sizeof(m_status),
                          "Build: queued %s (tick=%u)", sp->name, (unsigned)tick);
        } else {
            std::snprintf(m_status, sizeof(m_status),
                          "Build: queued structure #%u (tick=%u)",
                          (unsigned)m_structure_id, (unsigned)tick);
        }
    }
    return 1;
}

int DomGameBuildTool::commit_draw_spline(DomGameApp &app) {
    (void)app;
    /* Corridor/spline placement is not implemented in this prompt. */
    set_status("Build: spline placement not available (anchor contract)");
    clear_spline();
    return 0;
}

int DomGameBuildTool::handle_event(DomGameApp &app, const d_sys_event &ev) {
    if (m_mode == MODE_NONE) {
        return 0;
    }

    if (ev.type == D_SYS_EVENT_KEY_DOWN) {
        if (ev.u.key.key == D_SYS_KEY_Q) {
            rotate_step(-1);
            return 1;
        }
        if (ev.u.key.key == D_SYS_KEY_E) {
            rotate_step(+1);
            return 1;
        }
        return 0;
    }

    if (ev.type == D_SYS_EVENT_MOUSE_BUTTON_DOWN) {
        if (ev.u.mouse.button == 1u) {
            q32_32 wx = 0;
            q32_32 wy = 0;
            dom_screen_to_world_xy(app.camera(), m_mouse_x, m_mouse_y, &wx, &wy);

            if (m_mode == MODE_PLACE_STRUCTURE) {
                return commit_place_structure(app, wx, wy);
            } else if (m_mode == MODE_DRAW_SPLINE) {
                if (!m_spline_active) {
                    clear_spline();
                    m_spline_active = 1;
                }
                if (m_spline_node_count < 16u) {
                    d_spline_node n;
                    std::memset(&n, 0, sizeof(n));
                    n.x = wx;
                    n.y = wy;
                    n.z = 0;
                    m_spline_nodes[m_spline_node_count++] = n;
                    std::snprintf(m_status, sizeof(m_status),
                                  "Tool: spline node %u/%u (right-click to finish)",
                                  (unsigned)m_spline_node_count, 16u);
                } else {
                    set_status("Tool: max spline nodes reached (right-click to finish)");
                }
                return 1;
            }
        } else if (ev.u.mouse.button == 2u) {
            if (m_mode == MODE_DRAW_SPLINE && m_spline_active) {
                if (m_spline_node_count >= 2u) {
                    return commit_draw_spline(app);
                }
                clear_spline();
                set_status("Tool: spline cancelled");
                return 1;
            }
        }
    }

    return 0;
}

void DomGameBuildTool::render_overlay(const DomGameApp &app,
                                     d_gfx_cmd_buffer *cmd_buffer,
                                     i32 width,
                                     i32 height) const {
    d_gfx_color c;
    i32 mx = m_mouse_x;
    i32 my = m_mouse_y;

    if (!cmd_buffer) {
        return;
    }
    if (m_mode == MODE_NONE) {
        return;
    }

    c.a = 0xffu;
    c.r = 0xffu;
    c.g = 0xffu;
    c.b = 0xffu;

    /* Mouse marker */
    dom_emit_point(cmd_buffer, mx, my, 5, c);

    if (m_mode == MODE_PLACE_STRUCTURE) {
        dom_emit_outline(cmd_buffer, mx - 10, my - 10, 20, 20, 2, c);
        return;
    }

    if (m_mode == MODE_DRAW_SPLINE && m_spline_active && m_spline_node_count > 0u) {
        dgfx_line_segment_t segs[16];
        u16 seg_count = 0u;
        u16 i;
        for (i = 0u; i + 1u < m_spline_node_count && seg_count < 16u; ++i) {
            i32 x0, y0, x1, y1;
            dom_world_xy_to_screen(app.camera(), width, height,
                                   m_spline_nodes[i].x, m_spline_nodes[i].y, &x0, &y0);
            dom_world_xy_to_screen(app.camera(), width, height,
                                   m_spline_nodes[i + 1u].x, m_spline_nodes[i + 1u].y, &x1, &y1);
            segs[seg_count].x0 = x0;
            segs[seg_count].y0 = y0;
            segs[seg_count].x1 = x1;
            segs[seg_count].y1 = y1;
            segs[seg_count].color_rgba = 0xffaaaaaaU;
            segs[seg_count].thickness = 2;
            seg_count++;
        }
        if (seg_count < 16u) {
            i32 x0, y0;
            dom_world_xy_to_screen(app.camera(), width, height,
                                   m_spline_nodes[m_spline_node_count - 1u].x,
                                   m_spline_nodes[m_spline_node_count - 1u].y, &x0, &y0);
            segs[seg_count].x0 = x0;
            segs[seg_count].y0 = y0;
            segs[seg_count].x1 = mx;
            segs[seg_count].y1 = my;
            segs[seg_count].color_rgba = 0xffffffffU;
            segs[seg_count].thickness = 2;
            seg_count++;
        }
        (void)dgfx_cmd_emit((dgfx_cmd_buffer *)cmd_buffer,
                            (u16)DGFX_CMD_DRAW_LINES,
                            segs,
                            (u16)(seg_count * sizeof(segs[0])));

        for (i = 0u; i < m_spline_node_count; ++i) {
            i32 sx, sy;
            dom_world_xy_to_screen(app.camera(), width, height,
                                   m_spline_nodes[i].x, m_spline_nodes[i].y, &sx, &sy);
            dom_emit_point(cmd_buffer, sx, sy, 5, c);
        }
    }
}

} // namespace dom
