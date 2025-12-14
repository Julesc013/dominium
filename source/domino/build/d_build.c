#include <stdlib.h>
#include <string.h>

#include "core/d_subsystem.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"
#include "policy/d_policy.h"
#include "world/d_world_terrain.h"
#include "struct/d_struct.h"
#include "trans/d_trans.h"
#include "build/d_build.h"

#define DBUILD_MAX_WORLDS 8u

typedef struct dbuild_foundation_s {
    u32   struct_id;
    q16_16 down[4]; /* anchor_z - corner_z, in Q16.16 */
} dbuild_foundation;

typedef struct dbuild_world_state_s {
    d_world           *world;
    dbuild_foundation *foundations;
    u32                foundation_count;
    u32                foundation_capacity;
    int                in_use;
} dbuild_world_state;

static dbuild_world_state g_build_worlds[DBUILD_MAX_WORLDS];
static int g_build_registered = 0;

static void dbuild_set_err(char *buf, u32 buf_size, const char *msg) {
    u32 i;
    if (!buf || buf_size == 0u) {
        return;
    }
    if (!msg) {
        buf[0] = '\0';
        return;
    }
    for (i = 0u; i + 1u < buf_size && msg[i] != '\0'; ++i) {
        buf[i] = msg[i];
    }
    buf[i] = '\0';
}

static dbuild_world_state *dbuild_find_world(d_world *w) {
    u32 i;
    for (i = 0u; i < DBUILD_MAX_WORLDS; ++i) {
        if (g_build_worlds[i].in_use && g_build_worlds[i].world == w) {
            return &g_build_worlds[i];
        }
    }
    return (dbuild_world_state *)0;
}

static void dbuild_free_world_state(dbuild_world_state *st) {
    if (!st) {
        return;
    }
    if (st->foundations) {
        free(st->foundations);
    }
    memset(st, 0, sizeof(*st));
}

static dbuild_world_state *dbuild_get_or_create_world(d_world *w) {
    dbuild_world_state *st;
    u32 i;
    if (!w) {
        return (dbuild_world_state *)0;
    }
    st = dbuild_find_world(w);
    if (st) {
        return st;
    }
    for (i = 0u; i < DBUILD_MAX_WORLDS; ++i) {
        if (!g_build_worlds[i].in_use) {
            memset(&g_build_worlds[i], 0, sizeof(g_build_worlds[i]));
            g_build_worlds[i].world = w;
            g_build_worlds[i].in_use = 1;
            return &g_build_worlds[i];
        }
    }
    return (dbuild_world_state *)0;
}

static void dbuild_reset_world(d_world *w) {
    dbuild_world_state *st;
    if (!w) {
        return;
    }
    st = dbuild_get_or_create_world(w);
    if (!st) {
        return;
    }
    if (st->foundations) {
        free(st->foundations);
    }
    st->foundations = (dbuild_foundation *)0;
    st->foundation_count = 0u;
    st->foundation_capacity = 0u;
}

static int dbuild_reserve_foundations(dbuild_world_state *st, u32 needed) {
    dbuild_foundation *new_items;
    u32 new_cap;
    if (!st) {
        return -1;
    }
    if (needed <= st->foundation_capacity) {
        return 0;
    }
    new_cap = st->foundation_capacity ? st->foundation_capacity : 64u;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    new_items = (dbuild_foundation *)realloc(st->foundations, new_cap * sizeof(dbuild_foundation));
    if (!new_items) {
        return -1;
    }
    st->foundations = new_items;
    st->foundation_capacity = new_cap;
    return 0;
}

static q16_16 dbuild_q16_from_q32(q32_32 v) {
    i64 shifted = ((i64)v) >> (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
    if (shifted > (i64)2147483647L) return (q16_16)2147483647L;
    if (shifted < (i64)(-2147483647L - 1L)) return (q16_16)(-2147483647L - 1L);
    return (q16_16)(i32)shifted;
}

static u16 dbuild_yaw_steps_90(q16_16 yaw_turns_q16) {
    u32 step;
    u32 y = (u32)yaw_turns_q16;
    /* Quarter turn = 0x4000 (0.25); round to nearest. */
    step = (y + 0x2000u) >> 14;
    return (u16)(step & 3u);
}

static void dbuild_rotate_xy_90(u16 steps, q16_16 x, q16_16 y, q16_16 *out_x, q16_16 *out_y) {
    q16_16 rx = x;
    q16_16 ry = y;
    steps &= 3u;
    if (steps == 1u) {
        rx = (q16_16)(-y);
        ry = x;
    } else if (steps == 2u) {
        rx = (q16_16)(-x);
        ry = (q16_16)(-y);
    } else if (steps == 3u) {
        rx = y;
        ry = (q16_16)(-x);
    }
    if (out_x) *out_x = rx;
    if (out_y) *out_y = ry;
}

static void dbuild_parse_footprint(const d_proto_structure *sp, u32 *out_w, u32 *out_h) {
    u32 w = 1u;
    u32 h = 1u;
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;

    if (out_w) *out_w = 1u;
    if (out_h) *out_h = 1u;
    if (!sp) {
        return;
    }
    if (!sp->layout.ptr || sp->layout.len == 0u) {
        if (out_w) *out_w = w;
        if (out_h) *out_h = h;
        return;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(&sp->layout, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_STRUCT_LAYOUT_FOOTPRINT_W) {
            (void)d_tlv_kv_read_u32(&payload, &w);
        } else if (tag == D_TLV_STRUCT_LAYOUT_FOOTPRINT_H) {
            (void)d_tlv_kv_read_u32(&payload, &h);
        }
    }
    if (w == 0u) w = 1u;
    if (h == 0u) h = 1u;
    if (out_w) *out_w = w;
    if (out_h) *out_h = h;
}

static int dbuild_compute_foundation_down(
    d_world  *w,
    q32_32    pos_x,
    q32_32    pos_y,
    q16_16    yaw_turns_q16,
    u32       footprint_w,
    u32       footprint_h,
    q32_32   *out_anchor_z,
    q16_16    out_down[4]
) {
    q32_32 corners_x[4];
    q32_32 corners_y[4];
    q32_32 hz[4];
    q32_32 avg;
    u16 steps;
    u32 i;
    q16_16 hw16;
    q16_16 hh16;
    q16_16 ox[4];
    q16_16 oy[4];
    q16_16 rx;
    q16_16 ry;

    if (!w || !out_anchor_z || !out_down) {
        return -1;
    }

    /* Footprint extents around the anchor (center). */
    hw16 = (q16_16)((i32)(footprint_w << 16) / 2);
    hh16 = (q16_16)((i32)(footprint_h << 16) / 2);

    ox[0] = (q16_16)(-hw16); oy[0] = (q16_16)(-hh16);
    ox[1] = hw16;           oy[1] = (q16_16)(-hh16);
    ox[2] = hw16;           oy[2] = hh16;
    ox[3] = (q16_16)(-hw16); oy[3] = hh16;

    steps = dbuild_yaw_steps_90(yaw_turns_q16);
    for (i = 0u; i < 4u; ++i) {
        dbuild_rotate_xy_90(steps, ox[i], oy[i], &rx, &ry);
        corners_x[i] = pos_x + (((q32_32)rx) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS));
        corners_y[i] = pos_y + (((q32_32)ry) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS));
        hz[i] = 0;
        if (d_world_height_at(w, corners_x[i], corners_y[i], &hz[i]) != 0) {
            hz[i] = 0;
        }
    }

    avg = (q32_32)(((i64)hz[0] + (i64)hz[1] + (i64)hz[2] + (i64)hz[3]) / 4);
    *out_anchor_z = avg;

    for (i = 0u; i < 4u; ++i) {
        q32_32 dz = avg - hz[i];
        out_down[i] = dbuild_q16_from_q32(dz);
    }

    return 0;
}

static int dbuild_check_structure_overlap(d_world *w, q16_16 x, q16_16 y, u32 footprint_w, u32 footprint_h) {
    u32 i;
    u32 count;
    q16_16 hw = (q16_16)((i32)(footprint_w << 16) / 2);
    q16_16 hh = (q16_16)((i32)(footprint_h << 16) / 2);
    if (!w) {
        return 0;
    }
    count = d_struct_count(w);
    for (i = 0u; i < count; ++i) {
        const d_struct_instance *inst = d_struct_get_by_index(w, i);
        q16_16 dx;
        q16_16 dy;
        if (!inst) {
            continue;
        }
        dx = (q16_16)(inst->pos_x - x);
        dy = (q16_16)(inst->pos_y - y);
        if (dx < 0) dx = (q16_16)(-dx);
        if (dy < 0) dy = (q16_16)(-dy);
        if (dx < hw && dy < hh) {
            return 1;
        }
    }
    return 0;
}

int d_build_get_foundation_down(
    const d_world *w,
    u32            struct_id,
    q16_16         out_down[4]
) {
    dbuild_world_state *st;
    u32 i;
    if (!out_down) {
        return -1;
    }
    out_down[0] = out_down[1] = out_down[2] = out_down[3] = 0;
    if (!w || struct_id == 0u) {
        return -1;
    }
    st = dbuild_find_world((d_world *)w);
    if (!st) {
        return -1;
    }
    for (i = 0u; i < st->foundation_count; ++i) {
        if (st->foundations[i].struct_id == struct_id) {
            out_down[0] = st->foundations[i].down[0];
            out_down[1] = st->foundations[i].down[1];
            out_down[2] = st->foundations[i].down[2];
            out_down[3] = st->foundations[i].down[3];
            return 0;
        }
    }
    return -1;
}

static int dbuild_set_foundation_down(d_world *w, u32 struct_id, const q16_16 down[4]) {
    dbuild_world_state *st;
    u32 i;
    if (!w || struct_id == 0u || !down) {
        return -1;
    }
    st = dbuild_get_or_create_world(w);
    if (!st) {
        return -1;
    }
    for (i = 0u; i < st->foundation_count; ++i) {
        if (st->foundations[i].struct_id == struct_id) {
            memcpy(st->foundations[i].down, down, sizeof(q16_16) * 4u);
            return 0;
        }
    }
    if (dbuild_reserve_foundations(st, st->foundation_count + 1u) != 0) {
        return -1;
    }
    st->foundations[st->foundation_count].struct_id = struct_id;
    memcpy(st->foundations[st->foundation_count].down, down, sizeof(q16_16) * 4u);
    st->foundation_count += 1u;
    return 0;
}

static int dbuild_segment_length_q16(const d_spline_node *a, const d_spline_node *b, q16_16 *out_len) {
    q16_16 dx;
    q16_16 dy;
    q16_16 dz;
    i64 ddx;
    i64 ddy;
    i64 ddz;
    u64 sum;
    u64 bit;
    u64 res;
    u64 v;
    if (out_len) *out_len = 0;
    if (!a || !b || !out_len) {
        return -1;
    }
    dx = dbuild_q16_from_q32(b->x - a->x);
    dy = dbuild_q16_from_q32(b->y - a->y);
    dz = dbuild_q16_from_q32(b->z - a->z);
    ddx = (i64)dx;
    ddy = (i64)dy;
    ddz = (i64)dz;
    sum = (u64)(ddx * ddx) + (u64)(ddy * ddy) + (u64)(ddz * ddz);

    /* isqrt */
    v = sum;
    res = 0u;
    bit = (u64)1u << 62;
    while (bit > v) bit >>= 2;
    while (bit != 0u) {
        if (v >= res + bit) {
            v -= res + bit;
            res = (res >> 1) + bit;
        } else {
            res >>= 1;
        }
        bit >>= 2;
    }
    if (res > (u64)2147483647L) {
        *out_len = (q16_16)2147483647L;
    } else {
        *out_len = (q16_16)(i32)res;
    }
    return 0;
}

static q16_16 dbuild_q16_div(q16_16 num, q16_16 den) {
    if (den == 0) return 0;
    return (q16_16)(((i64)num << 16) / (i64)den);
}

static q16_16 dbuild_abs_q16(q16_16 v) {
    if (v < 0) {
        if (v == (q16_16)(-2147483647L - 1L)) return (q16_16)2147483647L;
        return (q16_16)(-v);
    }
    return v;
}

static void dbuild_prepare_spline_nodes(
    d_world               *w,
    const d_build_request *req,
    d_spline_node         *tmp_nodes,
    u16                   *out_node_count
) {
    u16 i;
    if (out_node_count) {
        *out_node_count = 0u;
    }
    if (!w || !req || !tmp_nodes || !out_node_count) {
        return;
    }
    if (req->spline_nodes && req->spline_node_count >= 2u) {
        u16 n = req->spline_node_count;
        if (n > 16u) n = 16u;
        for (i = 0u; i < n; ++i) {
            tmp_nodes[i] = req->spline_nodes[i];
            if (req->flags & D_BUILD_FLAG_SNAP_TERRAIN) {
                q32_32 hz = 0;
                (void)d_world_height_at(w, tmp_nodes[i].x, tmp_nodes[i].y, &hz);
                tmp_nodes[i].z = hz;
            }
        }
        *out_node_count = n;
        return;
    }

    /* Endpoints only. */
    tmp_nodes[0].x = req->pos_x;
    tmp_nodes[0].y = req->pos_y;
    tmp_nodes[0].z = req->pos_z;
    tmp_nodes[0].nx = tmp_nodes[0].ny = 0;
    tmp_nodes[0].nz = 0;
    tmp_nodes[1].x = req->pos2_x;
    tmp_nodes[1].y = req->pos2_y;
    tmp_nodes[1].z = req->pos2_z;
    tmp_nodes[1].nx = tmp_nodes[1].ny = 0;
    tmp_nodes[1].nz = 0;

    if (req->flags & D_BUILD_FLAG_SNAP_TERRAIN) {
        q32_32 hz0 = 0;
        q32_32 hz1 = 0;
        (void)d_world_height_at(w, tmp_nodes[0].x, tmp_nodes[0].y, &hz0);
        (void)d_world_height_at(w, tmp_nodes[1].x, tmp_nodes[1].y, &hz1);
        tmp_nodes[0].z = hz0;
        tmp_nodes[1].z = hz1;
    }
    *out_node_count = 2u;
}

static int dbuild_tlv_read_i32(const d_tlv_blob *payload, i32 *out) {
    if (!payload || !out || !payload->ptr || payload->len != 4u) {
        return -1;
    }
    memcpy(out, payload->ptr, sizeof(i32));
    return 0;
}

static int dbuild_find_nearest_struct_port(
    d_world *w,
    q32_32   px,
    q32_32   py,
    u16      desired_kind,
    u32     *out_struct_id,
    u16     *out_port_kind,
    u16     *out_port_index
) {
    const q16_16 radius = (q16_16)(1 << 16); /* 1m */
    const u64 radius2 = (u64)((i64)radius * (i64)radius);
    q16_16 px16;
    q16_16 py16;
    u64 best_d2 = (u64)0xFFFFFFFFFFFFFFFFULL;
    u32 best_struct = 0u;
    u16 best_kind = 0u;
    u16 best_index = 0u;
    u32 si;
    u32 scount;

    if (out_struct_id) *out_struct_id = 0u;
    if (out_port_kind) *out_port_kind = 0u;
    if (out_port_index) *out_port_index = 0u;
    if (!w) {
        return -1;
    }

    px16 = dbuild_q16_from_q32(px);
    py16 = dbuild_q16_from_q32(py);

    scount = d_struct_count(w);
    for (si = 0u; si < scount; ++si) {
        const d_struct_instance *inst = d_struct_get_by_index(w, si);
        const d_proto_structure *sp;
        u32 offset;
        u32 tag;
        d_tlv_blob payload;
        int rc;
        u16 port_index = 0u;

        if (!inst) {
            continue;
        }
        sp = d_content_get_structure(inst->proto_id);
        if (!sp || !sp->io.ptr || sp->io.len == 0u) {
            continue;
        }

        offset = 0u;
        while ((rc = d_tlv_kv_next(&sp->io, &offset, &tag, &payload)) == 0) {
            if (tag == D_TLV_STRUCT_IO_PORT) {
                u32 poff = 0u;
                u32 ptag = 0u;
                d_tlv_blob ppayload;
                u32 kind_u32 = 0u;
                i32 lx_i32 = 0;
                i32 ly_i32 = 0;
                u16 kind16;
                q16_16 lx;
                q16_16 ly;
                q16_16 rx;
                q16_16 ry;
                q16_16 wx;
                q16_16 wy;
                q16_16 dx;
                q16_16 dy;
                u64 d2;
                u16 steps;

                while (d_tlv_kv_next(&payload, &poff, &ptag, &ppayload) == 0) {
                    if (ptag == D_TLV_STRUCT_PORT_KIND) {
                        (void)d_tlv_kv_read_u32(&ppayload, &kind_u32);
                    } else if (ptag == D_TLV_STRUCT_PORT_POS_X) {
                        (void)dbuild_tlv_read_i32(&ppayload, &lx_i32);
                    } else if (ptag == D_TLV_STRUCT_PORT_POS_Y) {
                        (void)dbuild_tlv_read_i32(&ppayload, &ly_i32);
                    }
                }
                kind16 = (u16)kind_u32;
                if (desired_kind != 0u && kind16 != desired_kind) {
                    port_index += 1u;
                    continue;
                }

                lx = (q16_16)(lx_i32 << 16);
                ly = (q16_16)(ly_i32 << 16);
                steps = dbuild_yaw_steps_90(inst->rot_yaw);
                dbuild_rotate_xy_90(steps, lx, ly, &rx, &ry);
                wx = (q16_16)(inst->pos_x + rx);
                wy = (q16_16)(inst->pos_y + ry);

                dx = (q16_16)(wx - px16);
                dy = (q16_16)(wy - py16);
                if (dx < 0) dx = (q16_16)(-dx);
                if (dy < 0) dy = (q16_16)(-dy);
                d2 = (u64)((i64)dx * (i64)dx) + (u64)((i64)dy * (i64)dy);
                if (d2 <= radius2 && d2 < best_d2) {
                    best_d2 = d2;
                    best_struct = (u32)inst->id;
                    best_kind = kind16;
                    best_index = port_index;
                }

                port_index += 1u;
            }
        }
    }

    if (best_struct == 0u) {
        return -1;
    }
    if (out_struct_id) *out_struct_id = best_struct;
    if (out_port_kind) *out_port_kind = best_kind;
    if (out_port_index) *out_port_index = best_index;
    return 0;
}

int d_build_validate(
    d_world               *w,
    const d_build_request *req,
    char                  *err_buf,
    u32                    err_buf_size
) {
    if (err_buf && err_buf_size > 0u) {
        err_buf[0] = '\0';
    }
    if (!w || !req) {
        dbuild_set_err(err_buf, err_buf_size, "invalid args");
        return -1;
    }
    if (req->kind == D_BUILD_KIND_STRUCTURE) {
        const d_proto_structure *sp;
        u32 fw;
        u32 fh;
        q32_32 anchor_z;
        q16_16 down[4];
        q16_16 x16;
        q16_16 y16;

        if (req->structure_id == 0u) {
            dbuild_set_err(err_buf, err_buf_size, "missing structure_id");
            return -1;
        }
        sp = d_content_get_structure(req->structure_id);
        if (!sp) {
            dbuild_set_err(err_buf, err_buf_size, "unknown structure_id");
            return -1;
        }
        {
            d_policy_context ctx;
            d_policy_effect_result eff;
            memset(&ctx, 0, sizeof(ctx));
            ctx.org_id = req->owner_org;
            ctx.subject_kind = D_POLICY_SUBJECT_STRUCTURE;
            ctx.subject_id = (u32)req->structure_id;
            ctx.subject_tags = sp->tags;
            (void)d_policy_evaluate(&ctx, &eff);
            if (eff.allowed == 0u) {
                dbuild_set_err(err_buf, err_buf_size, "blocked by policy");
                return -1;
            }
        }

        dbuild_parse_footprint(sp, &fw, &fh);
        if (dbuild_compute_foundation_down(w, req->pos_x, req->pos_y, req->rot_yaw, fw, fh, &anchor_z, down) != 0) {
            dbuild_set_err(err_buf, err_buf_size, "terrain query failed");
            return -1;
        }
        x16 = dbuild_q16_from_q32(req->pos_x);
        y16 = dbuild_q16_from_q32(req->pos_y);
        if (dbuild_check_structure_overlap(w, x16, y16, fw, fh)) {
            dbuild_set_err(err_buf, err_buf_size, "overlaps existing structure");
            return -1;
        }
        return 0;
    } else if (req->kind == D_BUILD_KIND_SPLINE) {
        const d_proto_spline_profile *pp;
        d_spline_node nodes[16];
        u16 node_count;
        u16 i;

        if (req->spline_profile_id == 0u) {
            dbuild_set_err(err_buf, err_buf_size, "missing spline_profile_id");
            return -1;
        }
        pp = d_content_get_spline_profile(req->spline_profile_id);
        if (!pp) {
            dbuild_set_err(err_buf, err_buf_size, "unknown spline_profile_id");
            return -1;
        }
        {
            d_policy_context ctx;
            d_policy_effect_result eff;
            memset(&ctx, 0, sizeof(ctx));
            ctx.org_id = req->owner_org;
            ctx.subject_kind = D_POLICY_SUBJECT_SPLINE_PROFILE;
            ctx.subject_id = (u32)req->spline_profile_id;
            ctx.subject_tags = pp->tags;
            (void)d_policy_evaluate(&ctx, &eff);
            if (eff.allowed == 0u) {
                dbuild_set_err(err_buf, err_buf_size, "blocked by policy");
                return -1;
            }
        }
        dbuild_prepare_spline_nodes(w, req, nodes, &node_count);
        if (node_count < 2u) {
            dbuild_set_err(err_buf, err_buf_size, "spline requires >= 2 nodes");
            return -1;
        }

        for (i = 0u; (u32)i + 1u < (u32)node_count; ++i) {
            q16_16 seg_len;
            q16_16 grade;
            q16_16 dz;
            if (dbuild_segment_length_q16(&nodes[i], &nodes[i + 1u], &seg_len) != 0 || seg_len <= 0) {
                dbuild_set_err(err_buf, err_buf_size, "invalid spline segment");
                return -1;
            }
            dz = dbuild_q16_from_q32(nodes[i + 1u].z - nodes[i].z);
            dz = dbuild_abs_q16(dz);
            grade = dbuild_q16_div(dz, seg_len);
            if (pp->max_grade > 0 && grade > pp->max_grade) {
                dbuild_set_err(err_buf, err_buf_size, "slope exceeds max_grade");
                return -1;
            }
        }

        if (req->flags & D_BUILD_FLAG_REQUIRE_PORTS) {
            u32 sid0 = 0u;
            u32 sid1 = 0u;
            u16 pk0 = 0u;
            u16 pk1 = 0u;
            u16 pi0 = 0u;
            u16 pi1 = 0u;
            u16 start_kind0 = 0u;
            u16 start_kind1 = 0u;
            u16 end_kind0 = 0u;
            u16 end_kind1 = 0u;

            if (pp->type == (u16)D_SPLINE_TYPE_ITEM) {
                start_kind0 = (u16)D_STRUCT_PORT_SPLINE_ITEM_OUT;
                start_kind1 = (u16)D_STRUCT_PORT_ITEM_OUT;
                end_kind0 = (u16)D_STRUCT_PORT_SPLINE_ITEM_IN;
                end_kind1 = (u16)D_STRUCT_PORT_ITEM_IN;
            } else if (pp->type == (u16)D_SPLINE_TYPE_VEHICLE) {
                start_kind0 = (u16)D_STRUCT_PORT_SPLINE_VEHICLE;
                start_kind1 = 0u;
                end_kind0 = (u16)D_STRUCT_PORT_SPLINE_VEHICLE;
                end_kind1 = 0u;
            } else if (pp->type == (u16)D_SPLINE_TYPE_FLUID) {
                start_kind0 = (u16)D_STRUCT_PORT_FLUID_IO;
                start_kind1 = 0u;
                end_kind0 = (u16)D_STRUCT_PORT_FLUID_IO;
                end_kind1 = 0u;
            }

            if (start_kind0 == 0u) {
                dbuild_set_err(err_buf, err_buf_size, "profile has unknown type");
                return -1;
            }

            if (dbuild_find_nearest_struct_port(w, nodes[0].x, nodes[0].y, start_kind0, &sid0, &pk0, &pi0) != 0 &&
                (start_kind1 == 0u || dbuild_find_nearest_struct_port(w, nodes[0].x, nodes[0].y, start_kind1, &sid0, &pk0, &pi0) != 0)) {
                dbuild_set_err(err_buf, err_buf_size, "no compatible start port");
                return -1;
            }
            if (dbuild_find_nearest_struct_port(w, nodes[node_count - 1u].x, nodes[node_count - 1u].y, end_kind0, &sid1, &pk1, &pi1) != 0 &&
                (end_kind1 == 0u || dbuild_find_nearest_struct_port(w, nodes[node_count - 1u].x, nodes[node_count - 1u].y, end_kind1, &sid1, &pk1, &pi1) != 0)) {
                dbuild_set_err(err_buf, err_buf_size, "no compatible end port");
                return -1;
            }
        }

        return 0;
    }

    dbuild_set_err(err_buf, err_buf_size, "unknown build kind");
    return -1;
}

int d_build_commit(
    d_world               *w,
    const d_build_request *req,
    d_spline_id           *out_spline_id,
    u32                   *out_struct_eid
) {
    char err[128];
    int rc;

    if (out_spline_id) *out_spline_id = 0u;
    if (out_struct_eid) *out_struct_eid = 0u;
    if (!w || !req) {
        return -1;
    }
    err[0] = '\0';
    rc = d_build_validate(w, req, err, (u32)sizeof(err));
    if (rc != 0) {
        return rc;
    }

    if (req->kind == D_BUILD_KIND_STRUCTURE) {
        const d_proto_structure *sp;
        u32 fw;
        u32 fh;
        q32_32 anchor_z;
        q16_16 down[4];
        q16_16 x16;
        q16_16 y16;
        q16_16 z16;
        d_struct_instance_id sid;

        sp = d_content_get_structure(req->structure_id);
        if (!sp) {
            return -1;
        }
        dbuild_parse_footprint(sp, &fw, &fh);
        if (dbuild_compute_foundation_down(w, req->pos_x, req->pos_y, req->rot_yaw, fw, fh, &anchor_z, down) != 0) {
            return -1;
        }

        x16 = dbuild_q16_from_q32(req->pos_x);
        y16 = dbuild_q16_from_q32(req->pos_y);
        z16 = dbuild_q16_from_q32(anchor_z);
        sid = d_struct_create(w, req->structure_id, x16, y16, z16, req->rot_yaw);
        if (sid == 0u) {
            return -1;
        }
        {
            d_struct_instance *inst = d_struct_get_mutable(w, sid);
            if (inst) {
                inst->owner_org = req->owner_org;
            }
        }
        (void)dbuild_set_foundation_down(w, (u32)sid, down);

        if (out_struct_eid) {
            *out_struct_eid = (u32)sid;
        }
        return 0;
    } else if (req->kind == D_BUILD_KIND_SPLINE) {
        d_spline_node nodes[16];
        u16 node_count;
        d_spline_id sid;
        const d_proto_spline_profile *pp;

        dbuild_prepare_spline_nodes(w, req, nodes, &node_count);
        if (node_count < 2u) {
            return -1;
        }
        pp = d_content_get_spline_profile(req->spline_profile_id);
        if (!pp) {
            return -1;
        }
        sid = d_trans_spline_create(w, nodes, node_count, req->spline_profile_id, 0u, req->owner_org);
        if (sid == 0u) {
            return -1;
        }
        {
            u32 sid0 = 0u;
            u32 sid1 = 0u;
            u16 pk0 = 0u;
            u16 pk1 = 0u;
            u16 pi0 = 0u;
            u16 pi1 = 0u;
            u16 start_kind0 = 0u;
            u16 start_kind1 = 0u;
            u16 end_kind0 = 0u;
            u16 end_kind1 = 0u;

            if (pp->type == (u16)D_SPLINE_TYPE_ITEM) {
                start_kind0 = (u16)D_STRUCT_PORT_SPLINE_ITEM_OUT;
                start_kind1 = (u16)D_STRUCT_PORT_ITEM_OUT;
                end_kind0 = (u16)D_STRUCT_PORT_SPLINE_ITEM_IN;
                end_kind1 = (u16)D_STRUCT_PORT_ITEM_IN;
            } else if (pp->type == (u16)D_SPLINE_TYPE_VEHICLE) {
                start_kind0 = (u16)D_STRUCT_PORT_SPLINE_VEHICLE;
                start_kind1 = 0u;
                end_kind0 = (u16)D_STRUCT_PORT_SPLINE_VEHICLE;
                end_kind1 = 0u;
            } else if (pp->type == (u16)D_SPLINE_TYPE_FLUID) {
                start_kind0 = (u16)D_STRUCT_PORT_FLUID_IO;
                start_kind1 = 0u;
                end_kind0 = (u16)D_STRUCT_PORT_FLUID_IO;
                end_kind1 = 0u;
            }

            if (start_kind0 != 0u) {
                if (dbuild_find_nearest_struct_port(w, nodes[0].x, nodes[0].y, start_kind0, &sid0, &pk0, &pi0) != 0) {
                    if (start_kind1 != 0u) {
                        (void)dbuild_find_nearest_struct_port(w, nodes[0].x, nodes[0].y, start_kind1, &sid0, &pk0, &pi0);
                    }
                }
                if (dbuild_find_nearest_struct_port(w, nodes[node_count - 1u].x, nodes[node_count - 1u].y, end_kind0, &sid1, &pk1, &pi1) != 0) {
                    if (end_kind1 != 0u) {
                        (void)dbuild_find_nearest_struct_port(w, nodes[node_count - 1u].x, nodes[node_count - 1u].y, end_kind1, &sid1, &pk1, &pi1);
                    }
                }
            }
            (void)d_trans_spline_set_endpoints(w, sid, sid0, pk0, pi0, sid1, pk1, pi1);
        }
        if (out_spline_id) {
            *out_spline_id = sid;
        }
        return 0;
    }

    return -1;
}

static int dbuild_save_instance(d_world *w, d_tlv_blob *out) {
    dbuild_world_state *st;
    u32 version;
    u32 total;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;

    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    if (!w) {
        return 0;
    }

    st = dbuild_find_world(w);
    if (!st || st->foundation_count == 0u) {
        return 0;
    }

    version = 1u;
    total = 0u;
    total += 4u; /* version */
    total += 4u; /* count */
    total += st->foundation_count * (sizeof(u32) + sizeof(q16_16) * 4u);

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &version, sizeof(u32)); dst += 4u;
    memcpy(dst, &st->foundation_count, sizeof(u32)); dst += 4u;
    for (i = 0u; i < st->foundation_count; ++i) {
        memcpy(dst, &st->foundations[i].struct_id, sizeof(u32)); dst += sizeof(u32);
        memcpy(dst, st->foundations[i].down, sizeof(q16_16) * 4u); dst += sizeof(q16_16) * 4u;
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int dbuild_load_instance(d_world *w, const d_tlv_blob *in) {
    dbuild_world_state *st;
    const unsigned char *ptr;
    u32 remaining;
    u32 version;
    u32 count;
    u32 i;

    if (!w || !in) {
        return -1;
    }
    if (in->len == 0u) {
        return 0;
    }
    if (!in->ptr || in->len < 8u) {
        return -1;
    }

    st = dbuild_get_or_create_world(w);
    if (!st) {
        return -1;
    }
    dbuild_reset_world(w);

    ptr = in->ptr;
    remaining = in->len;
    memcpy(&version, ptr, sizeof(u32)); ptr += 4u; remaining -= 4u;
    if (version != 1u) {
        return -1;
    }
    memcpy(&count, ptr, sizeof(u32)); ptr += 4u; remaining -= 4u;

    if (count > 0u) {
        u32 need = count * (sizeof(u32) + sizeof(q16_16) * 4u);
        if (remaining < need) {
            return -1;
        }
        if (dbuild_reserve_foundations(st, count) != 0) {
            return -1;
        }
        for (i = 0u; i < count; ++i) {
            memcpy(&st->foundations[i].struct_id, ptr, sizeof(u32)); ptr += sizeof(u32);
            memcpy(st->foundations[i].down, ptr, sizeof(q16_16) * 4u); ptr += sizeof(q16_16) * 4u;
        }
        st->foundation_count = count;
    }
    return 0;
}

static int dbuild_save_chunk(d_world *w, d_chunk *chunk, d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int dbuild_load_chunk(d_world *w, d_chunk *chunk, const d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static void dbuild_init_instance_subsys(d_world *w) {
    dbuild_reset_world(w);
}

static void dbuild_tick_stub(d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static void dbuild_register_models(void) {
    /* Future: construction models. */
}

static void dbuild_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_build_subsystem = {
    D_SUBSYS_BUILD,
    "build",
    2u,
    dbuild_register_models,
    dbuild_load_protos,
    dbuild_init_instance_subsys,
    dbuild_tick_stub,
    dbuild_save_chunk,
    dbuild_load_chunk,
    dbuild_save_instance,
    dbuild_load_instance
};

void d_build_register_subsystem(void) {
    if (g_build_registered) {
        return;
    }
    if (d_subsystem_register(&g_build_subsystem) == 0) {
        g_build_registered = 1;
    }
}

void d_build_shutdown(d_world *w) {
    dbuild_world_state *st;
    if (!w) {
        return;
    }
    st = dbuild_find_world(w);
    if (!st) {
        return;
    }
    dbuild_free_world_state(st);
}
