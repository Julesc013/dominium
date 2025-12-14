#include <stdlib.h>
#include <string.h>

#include "core/d_subsystem.h"
#include "content/d_content.h"
#include "content/d_content_extra.h"
#include "core/d_container_state.h"
#include "struct/d_struct.h"
#include "trans/d_trans.h"

#define DTRANS_MAX_WORLDS 8u

#define DTRANS_I32_MAX ((i32)2147483647L)
#define DTRANS_I32_MIN ((i32)(-2147483647L - 1L))

typedef struct dtrans_world_state_s {
    d_world *world;

    d_spline_node     *nodes;
    u32                node_count;
    u32                node_capacity;

    d_spline_instance *splines;
    u32                spline_count;
    u32                spline_capacity;

    d_mover           *movers;
    u32                mover_count;
    u32                mover_capacity;

    d_spline_id        next_spline_id;
    d_mover_id         next_mover_id;

    int                in_use;
} dtrans_world_state;

static dtrans_world_state g_trans_worlds[DTRANS_MAX_WORLDS];
static int g_trans_registered = 0;

static u64 dtrans_isqrt_u64(u64 v) {
    u64 res = 0;
    u64 bit = (u64)1u << 62;
    while (bit > v) {
        bit >>= 2;
    }
    while (bit != 0u) {
        if (v >= res + bit) {
            v -= res + bit;
            res = (res >> 1) + bit;
        } else {
            res >>= 1;
        }
        bit >>= 2;
    }
    return res;
}

static q16_16 dtrans_q16_from_q32(q32_32 v) {
    i64 shifted = ((i64)v) >> (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
    if (shifted > (i64)DTRANS_I32_MAX) return (q16_16)DTRANS_I32_MAX;
    if (shifted < (i64)DTRANS_I32_MIN) return (q16_16)DTRANS_I32_MIN;
    return (q16_16)shifted;
}

static q16_16 dtrans_clamp_q16(q16_16 v, q16_16 lo, q16_16 hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static q16_16 dtrans_q16_div(q16_16 num, q16_16 den);
static q16_16 dtrans_q16_mul(q16_16 a, q16_16 b);
static q16_16 dtrans_abs_q16(q16_16 v);

static dtrans_world_state *dtrans_find_world(d_world *w) {
    u32 i;
    for (i = 0u; i < DTRANS_MAX_WORLDS; ++i) {
        if (g_trans_worlds[i].in_use && g_trans_worlds[i].world == w) {
            return &g_trans_worlds[i];
        }
    }
    return (dtrans_world_state *)0;
}

static void dtrans_free_world_state(dtrans_world_state *st) {
    if (!st) {
        return;
    }
    if (st->nodes) {
        free(st->nodes);
    }
    if (st->splines) {
        free(st->splines);
    }
    if (st->movers) {
        free(st->movers);
    }
    memset(st, 0, sizeof(*st));
}

static dtrans_world_state *dtrans_get_or_create_world(d_world *w) {
    dtrans_world_state *st;
    u32 i;
    if (!w) {
        return (dtrans_world_state *)0;
    }
    st = dtrans_find_world(w);
    if (st) {
        return st;
    }
    for (i = 0u; i < DTRANS_MAX_WORLDS; ++i) {
        if (!g_trans_worlds[i].in_use) {
            memset(&g_trans_worlds[i], 0, sizeof(g_trans_worlds[i]));
            g_trans_worlds[i].world = w;
            g_trans_worlds[i].next_spline_id = 1u;
            g_trans_worlds[i].next_mover_id = 1u;
            g_trans_worlds[i].in_use = 1;
            return &g_trans_worlds[i];
        }
    }
    return (dtrans_world_state *)0;
}

static int dtrans_reserve_nodes(dtrans_world_state *st, u32 needed) {
    d_spline_node *new_nodes;
    u32 new_cap;
    if (!st) {
        return -1;
    }
    if (needed <= st->node_capacity) {
        return 0;
    }
    new_cap = st->node_capacity ? st->node_capacity : 256u;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    new_nodes = (d_spline_node *)realloc(st->nodes, new_cap * sizeof(d_spline_node));
    if (!new_nodes) {
        return -1;
    }
    st->nodes = new_nodes;
    st->node_capacity = new_cap;
    return 0;
}

static int dtrans_reserve_splines(dtrans_world_state *st, u32 needed) {
    d_spline_instance *new_splines;
    u32 new_cap;
    if (!st) {
        return -1;
    }
    if (needed <= st->spline_capacity) {
        return 0;
    }
    new_cap = st->spline_capacity ? st->spline_capacity : 64u;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    new_splines = (d_spline_instance *)realloc(st->splines, new_cap * sizeof(d_spline_instance));
    if (!new_splines) {
        return -1;
    }
    st->splines = new_splines;
    st->spline_capacity = new_cap;
    return 0;
}

static int dtrans_reserve_movers(dtrans_world_state *st, u32 needed) {
    d_mover *new_movers;
    u32 new_cap;
    if (!st) {
        return -1;
    }
    if (needed <= st->mover_capacity) {
        return 0;
    }
    new_cap = st->mover_capacity ? st->mover_capacity : 128u;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    new_movers = (d_mover *)realloc(st->movers, new_cap * sizeof(d_mover));
    if (!new_movers) {
        return -1;
    }
    st->movers = new_movers;
    st->mover_capacity = new_cap;
    return 0;
}

static q16_16 dtrans_segment_length_q16(const d_spline_node *a, const d_spline_node *b) {
    q16_16 dx;
    q16_16 dy;
    q16_16 dz;
    i64 ddx;
    i64 ddy;
    i64 ddz;
    u64 sum;
    u64 root;
    if (!a || !b) {
        return 0;
    }
    dx = dtrans_q16_from_q32((q32_32)(b->x - a->x));
    dy = dtrans_q16_from_q32((q32_32)(b->y - a->y));
    dz = dtrans_q16_from_q32((q32_32)(b->z - a->z));
    ddx = (i64)dx;
    ddy = (i64)dy;
    ddz = (i64)dz;
    sum = (u64)(ddx * ddx) + (u64)(ddy * ddy) + (u64)(ddz * ddz);
    root = dtrans_isqrt_u64(sum);
    if (root > (u64)DTRANS_I32_MAX) {
        return (q16_16)DTRANS_I32_MAX;
    }
    return (q16_16)(i32)root;
}

static q16_16 dtrans_polyline_length_q16(const d_spline_node *nodes, u16 node_count) {
    u16 i;
    i64 total;
    if (!nodes || node_count < 2u) {
        return 0;
    }
    total = 0;
    for (i = 0u; (u32)i + 1u < (u32)node_count; ++i) {
        q16_16 seg = dtrans_segment_length_q16(&nodes[i], &nodes[i + 1u]);
        total += (i64)seg;
        if (total > (i64)DTRANS_I32_MAX) {
            total = (i64)DTRANS_I32_MAX;
            break;
        }
    }
    return (q16_16)(i32)total;
}

static d_spline_instance *dtrans_find_spline(dtrans_world_state *st, d_spline_id id) {
    u32 i;
    if (!st || !id) {
        return (d_spline_instance *)0;
    }
    for (i = 0u; i < st->spline_count; ++i) {
        if (st->splines[i].id == id) {
            return &st->splines[i];
        }
    }
    return (d_spline_instance *)0;
}

static d_mover *dtrans_find_mover(dtrans_world_state *st, d_mover_id id) {
    u32 i;
    if (!st || !id) {
        return (d_mover *)0;
    }
    for (i = 0u; i < st->mover_count; ++i) {
        if (st->movers[i].id == id) {
            return &st->movers[i];
        }
    }
    return (d_mover *)0;
}

int d_trans_init(d_world *w) {
    dtrans_world_state *st;
    if (!w) {
        return -1;
    }
    st = dtrans_get_or_create_world(w);
    if (!st) {
        return -1;
    }
    /* Reset per-world runtime state. */
    if (st->nodes) {
        free(st->nodes);
    }
    if (st->splines) {
        free(st->splines);
    }
    if (st->movers) {
        free(st->movers);
    }
    st->nodes = (d_spline_node *)0;
    st->node_count = 0u;
    st->node_capacity = 0u;
    st->splines = (d_spline_instance *)0;
    st->spline_count = 0u;
    st->spline_capacity = 0u;
    st->movers = (d_mover *)0;
    st->mover_count = 0u;
    st->mover_capacity = 0u;
    st->next_spline_id = 1u;
    st->next_mover_id = 1u;
    return 0;
}

void d_trans_shutdown(d_world *w) {
    dtrans_world_state *st;
    if (!w) {
        return;
    }
    st = dtrans_find_world(w);
    if (!st) {
        return;
    }
    dtrans_free_world_state(st);
}

static d_spline_id dtrans_spline_create_with_id(
    d_world                 *w,
    const d_spline_node     *nodes,
    u16                      node_count,
    d_spline_profile_id      profile_id,
    d_spline_flags           flags,
    d_org_id                 owner_org,
    d_spline_id              forced_id
) {
    dtrans_world_state *st;
    d_spline_instance inst;
    u32 start_index;
    u32 i;

    if (!w || !nodes || node_count < 2u || profile_id == 0u) {
        return 0u;
    }
    if (node_count > 0xFFFFu) {
        return 0u;
    }

    st = dtrans_get_or_create_world(w);
    if (!st) {
        return 0u;
    }
    if (st->node_count > 0xFFFFu) {
        return 0u;
    }
    if ((u32)node_count > (0xFFFFu - (u32)st->node_count)) {
        return 0u;
    }

    if (dtrans_reserve_nodes(st, st->node_count + (u32)node_count) != 0) {
        return 0u;
    }
    if (dtrans_reserve_splines(st, st->spline_count + 1u) != 0) {
        return 0u;
    }

    start_index = st->node_count;
    for (i = 0u; i < (u32)node_count; ++i) {
        st->nodes[start_index + i] = nodes[i];
    }
    st->node_count += (u32)node_count;

    memset(&inst, 0, sizeof(inst));
    inst.id = forced_id ? forced_id : st->next_spline_id++;
    inst.profile_id = profile_id;
    inst.owner_org = owner_org;
    inst.flags = flags;
    inst.node_start_index = (u16)start_index;
    inst.node_count = node_count;
    inst.length = dtrans_polyline_length_q16(nodes, node_count);

    st->splines[st->spline_count++] = inst;

    if (forced_id && forced_id >= st->next_spline_id) {
        st->next_spline_id = forced_id + 1u;
    }
    return inst.id;
}

d_spline_id d_trans_spline_create(
    d_world                 *w,
    const d_spline_node     *nodes,
    u16                      node_count,
    d_spline_profile_id      profile_id,
    d_spline_flags           flags,
    d_org_id                 owner_org
) {
    return dtrans_spline_create_with_id(w, nodes, node_count, profile_id, flags, owner_org, 0u);
}

int d_trans_spline_destroy(d_world *w, d_spline_id id) {
    dtrans_world_state *st;
    u32 i;
    if (!w || id == 0u) {
        return -1;
    }
    st = dtrans_find_world(w);
    if (!st) {
        return -1;
    }

    /* Remove movers on this spline first. */
    for (i = 0u; i < st->mover_count; ) {
        if (st->movers[i].spline_id == id) {
            st->movers[i] = st->movers[st->mover_count - 1u];
            st->mover_count -= 1u;
            continue;
        }
        i += 1u;
    }

    for (i = 0u; i < st->spline_count; ++i) {
        if (st->splines[i].id == id) {
            st->splines[i] = st->splines[st->spline_count - 1u];
            st->spline_count -= 1u;
            return 0;
        }
    }
    return -1;
}

int d_trans_spline_get(const d_world *w, d_spline_id id, d_spline_instance *out) {
    dtrans_world_state *st;
    d_spline_instance *inst;
    if (!w || !out || id == 0u) {
        return -1;
    }
    st = dtrans_find_world((d_world *)w);
    if (!st) {
        return -1;
    }
    inst = dtrans_find_spline(st, id);
    if (!inst) {
        return -1;
    }
    *out = *inst;
    return 0;
}

int d_trans_spline_set_endpoints(
    d_world     *w,
    d_spline_id  spline_id,
    u32          endpoint_a_eid,
    u16          endpoint_a_port_kind,
    u16          endpoint_a_port_index,
    u32          endpoint_b_eid,
    u16          endpoint_b_port_kind,
    u16          endpoint_b_port_index
) {
    dtrans_world_state *st;
    d_spline_instance *spline;
    if (!w || spline_id == 0u) {
        return -1;
    }
    st = dtrans_find_world(w);
    if (!st) {
        return -1;
    }
    spline = dtrans_find_spline(st, spline_id);
    if (!spline) {
        return -1;
    }
    spline->endpoint_a_eid = endpoint_a_eid;
    spline->endpoint_a_port_kind = endpoint_a_port_kind;
    spline->endpoint_a_port_index = endpoint_a_port_index;
    spline->endpoint_b_eid = endpoint_b_eid;
    spline->endpoint_b_port_kind = endpoint_b_port_kind;
    spline->endpoint_b_port_index = endpoint_b_port_index;
    return 0;
}

u32 d_trans_spline_count(const d_world *w) {
    dtrans_world_state *st;
    if (!w) {
        return 0u;
    }
    st = dtrans_find_world((d_world *)w);
    if (!st) {
        return 0u;
    }
    return st->spline_count;
}

int d_trans_spline_get_by_index(const d_world *w, u32 index, d_spline_instance *out) {
    dtrans_world_state *st;
    if (!w || !out) {
        return -1;
    }
    st = dtrans_find_world((d_world *)w);
    if (!st || index >= st->spline_count) {
        return -1;
    }
    *out = st->splines[index];
    return 0;
}

int d_trans_spline_copy_nodes(
    const d_world     *w,
    u16                node_start_index,
    u16                node_count,
    d_spline_node     *out_nodes,
    u16                out_capacity,
    u16               *out_count
) {
    dtrans_world_state *st;
    u32 i;
    u32 start;
    u32 count;

    if (out_count) {
        *out_count = 0u;
    }
    if (!w || !out_nodes || !out_count) {
        return -1;
    }
    st = dtrans_find_world((d_world *)w);
    if (!st || !st->nodes) {
        return -1;
    }
    start = (u32)node_start_index;
    count = (u32)node_count;
    if (count > (u32)out_capacity) {
        count = (u32)out_capacity;
    }
    if (start >= st->node_count) {
        return -1;
    }
    if (count > st->node_count - start) {
        count = st->node_count - start;
    }
    for (i = 0u; i < count; ++i) {
        out_nodes[i] = st->nodes[start + i];
    }
    *out_count = (u16)count;
    return 0;
}

int d_trans_profile_resolve(
    const d_world             *w,
    d_spline_profile_id        profile_id,
    d_spline_profile_runtime  *out
) {
    const d_proto_spline_profile *p;
    (void)w;

    if (!out || profile_id == 0u) {
        return -1;
    }
    p = d_content_get_spline_profile(profile_id);
    if (!p) {
        memset(out, 0, sizeof(*out));
        return -1;
    }

    memset(out, 0, sizeof(*out));
    out->id = p->id;
    out->type = (u16)p->type;
    out->flags = (u16)p->flags;
    out->base_speed = p->base_speed;
    out->max_grade = p->max_grade;
    out->capacity = p->capacity;
    out->tags = p->tags;
    out->params = p->params;
    return 0;
}

int d_trans_spline_sample_pos(
    const d_world *w,
    d_spline_id    spline_id,
    q16_16         param,
    q32_32        *out_x,
    q32_32        *out_y,
    q32_32        *out_z
) {
    dtrans_world_state *st;
    d_spline_instance *spline;
    q16_16 target;
    q16_16 acc;
    u16 i;

    if (out_x) *out_x = 0;
    if (out_y) *out_y = 0;
    if (out_z) *out_z = 0;
    if (!w || spline_id == 0u) {
        return -1;
    }

    st = dtrans_find_world((d_world *)w);
    if (!st) {
        return -1;
    }
    spline = dtrans_find_spline(st, spline_id);
    if (!spline || spline->node_count < 2u || spline->length <= 0) {
        return -1;
    }
    if (!st->nodes) {
        return -1;
    }
    if ((u32)spline->node_start_index + (u32)spline->node_count > st->node_count) {
        return -1;
    }

    param = dtrans_clamp_q16(param, 0, (q16_16)(1 << 16));
    target = dtrans_q16_mul(param, spline->length);
    acc = 0;

    for (i = 0u; (u32)i + 1u < (u32)spline->node_count; ++i) {
        const d_spline_node *a = &st->nodes[(u32)spline->node_start_index + (u32)i];
        const d_spline_node *b = &st->nodes[(u32)spline->node_start_index + (u32)i + 1u];
        q16_16 seg_len = dtrans_segment_length_q16(a, b);
        if (seg_len <= 0) {
            continue;
        }
        if (target <= (q16_16)((i64)acc + (i64)seg_len)) {
            q16_16 local_t;
            q16_16 ax, ay, az;
            q16_16 bx, by, bz;
            q16_16 dx, dy, dz;
            q16_16 ix, iy, iz;

            local_t = dtrans_q16_div((q16_16)(target - acc), seg_len);
            local_t = dtrans_clamp_q16(local_t, 0, (q16_16)(1 << 16));

            ax = dtrans_q16_from_q32(a->x);
            ay = dtrans_q16_from_q32(a->y);
            az = dtrans_q16_from_q32(a->z);
            bx = dtrans_q16_from_q32(b->x);
            by = dtrans_q16_from_q32(b->y);
            bz = dtrans_q16_from_q32(b->z);

            dx = (q16_16)(bx - ax);
            dy = (q16_16)(by - ay);
            dz = (q16_16)(bz - az);

            ix = (q16_16)((i64)ax + ((i64)dtrans_q16_mul(dx, local_t)));
            iy = (q16_16)((i64)ay + ((i64)dtrans_q16_mul(dy, local_t)));
            iz = (q16_16)((i64)az + ((i64)dtrans_q16_mul(dz, local_t)));

            if (out_x) *out_x = ((q32_32)ix) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
            if (out_y) *out_y = ((q32_32)iy) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
            if (out_z) *out_z = ((q32_32)iz) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
            return 0;
        }
        acc = (q16_16)((i64)acc + (i64)seg_len);
    }

    /* Fallback to last node. */
    {
        const d_spline_node *last = &st->nodes[(u32)spline->node_start_index + (u32)spline->node_count - 1u];
        if (out_x) *out_x = last->x;
        if (out_y) *out_y = last->y;
        if (out_z) *out_z = last->z;
    }
    return 0;
}

static d_mover_id dtrans_mover_create_with_id(d_world *w, const d_mover *init, d_mover_id forced_id) {
    dtrans_world_state *st;
    d_mover m;

    if (!w || !init) {
        return 0u;
    }
    if (init->kind == D_MOVER_KIND_NONE) {
        return 0u;
    }
    if (init->spline_id == 0u) {
        return 0u;
    }
    st = dtrans_get_or_create_world(w);
    if (!st) {
        return 0u;
    }
    if (!dtrans_find_spline(st, init->spline_id)) {
        return 0u;
    }
    if (dtrans_reserve_movers(st, st->mover_count + 1u) != 0) {
        return 0u;
    }

    m = *init;
    m.id = forced_id ? forced_id : st->next_mover_id++;
    if (m.param < 0) {
        m.param = 0;
    }
    if (m.param > (q16_16)(1 << 16)) {
        m.param = (q16_16)(1 << 16);
    }

    st->movers[st->mover_count++] = m;
    if (forced_id && forced_id >= st->next_mover_id) {
        st->next_mover_id = forced_id + 1u;
    }
    return m.id;
}

d_mover_id d_trans_mover_create(d_world *w, const d_mover *init) {
    return dtrans_mover_create_with_id(w, init, 0u);
}

int d_trans_mover_destroy(d_world *w, d_mover_id id) {
    dtrans_world_state *st;
    u32 i;
    if (!w || id == 0u) {
        return -1;
    }
    st = dtrans_find_world(w);
    if (!st) {
        return -1;
    }
    for (i = 0u; i < st->mover_count; ++i) {
        if (st->movers[i].id == id) {
            st->movers[i] = st->movers[st->mover_count - 1u];
            st->mover_count -= 1u;
            return 0;
        }
    }
    return -1;
}

int d_trans_mover_get(const d_world *w, d_mover_id id, d_mover *out) {
    dtrans_world_state *st;
    d_mover *m;
    if (!w || !out || id == 0u) {
        return -1;
    }
    st = dtrans_find_world((d_world *)w);
    if (!st) {
        return -1;
    }
    m = dtrans_find_mover(st, id);
    if (!m) {
        return -1;
    }
    *out = *m;
    return 0;
}

int d_trans_mover_update(d_world *w, const d_mover *m) {
    dtrans_world_state *st;
    d_mover *dst;
    if (!w || !m || m->id == 0u) {
        return -1;
    }
    st = dtrans_find_world(w);
    if (!st) {
        return -1;
    }
    dst = dtrans_find_mover(st, m->id);
    if (!dst) {
        return -1;
    }
    if (m->spline_id == 0u || !dtrans_find_spline(st, m->spline_id)) {
        return -1;
    }
    *dst = *m;
    dst->param = dtrans_clamp_q16(dst->param, 0, (q16_16)(1 << 16));
    return 0;
}

u32 d_trans_mover_count(const d_world *w) {
    dtrans_world_state *st;
    if (!w) {
        return 0u;
    }
    st = dtrans_find_world((d_world *)w);
    if (!st) {
        return 0u;
    }
    return st->mover_count;
}

int d_trans_mover_get_by_index(const d_world *w, u32 index, d_mover *out) {
    dtrans_world_state *st;
    if (!w || !out) {
        return -1;
    }
    st = dtrans_find_world((d_world *)w);
    if (!st || index >= st->mover_count) {
        return -1;
    }
    *out = st->movers[index];
    return 0;
}

static q16_16 dtrans_q16_div(q16_16 num, q16_16 den) {
    i64 n;
    i64 d;
    if (den == 0) {
        return 0;
    }
    n = (i64)num;
    d = (i64)den;
    return (q16_16)((n << 16) / d);
}

static q16_16 dtrans_q16_mul(q16_16 a, q16_16 b) {
    return (q16_16)(((i64)a * (i64)b) >> 16);
}

static q16_16 dtrans_abs_q16(q16_16 v) {
    if (v < 0) {
        if (v == DTRANS_I32_MIN) return (q16_16)DTRANS_I32_MAX;
        return (q16_16)(-v);
    }
    return v;
}

static q16_16 dtrans_spline_grade_q16(dtrans_world_state *st, const d_spline_instance *spline) {
    d_spline_node a;
    d_spline_node b;
    q16_16 dz;
    q16_16 len;
    if (!st || !spline || spline->node_count < 2u) {
        return 0;
    }
    if (!st->nodes) {
        return 0;
    }
    if ((u32)spline->node_start_index + (u32)spline->node_count > st->node_count) {
        return 0;
    }
    a = st->nodes[spline->node_start_index];
    b = st->nodes[(u32)spline->node_start_index + (u32)spline->node_count - 1u];
    dz = dtrans_q16_from_q32((q32_32)(b.z - a.z));
    dz = dtrans_abs_q16(dz);
    len = spline->length;
    if (len <= 0) {
        return 0;
    }
    return dtrans_q16_div(dz, len);
}

void d_trans_mover_tick(d_world *w, u32 ticks) {
    dtrans_world_state *st;
    u32 i;

    if (!w || ticks == 0u) {
        return;
    }
    st = dtrans_find_world(w);
    if (!st) {
        return;
    }

    i = 0u;
    while (i < st->mover_count) {
        d_mover *m = &st->movers[i];
        d_spline_instance *spline;
        d_spline_profile_runtime prof;
        q16_16 speed_param;
        q16_16 grade;
        q16_16 speed;
        q16_16 scale;
        q16_16 ratio;
        i64 delta;
        i64 new_param;
        int consumed = 0;

        spline = dtrans_find_spline(st, m->spline_id);
        if (!spline || spline->length <= 0) {
            i += 1u;
            continue;
        }
        if (d_trans_profile_resolve(w, spline->profile_id, &prof) != 0) {
            i += 1u;
            continue;
        }

        speed = prof.base_speed;
        grade = dtrans_spline_grade_q16(st, spline);
        if (prof.max_grade > 0) {
            if (grade >= prof.max_grade) {
                speed = 0;
            } else {
                ratio = dtrans_q16_div(grade, prof.max_grade);
                /* scale = 1 - 0.5*ratio */
                scale = (q16_16)((1 << 16) - (ratio >> 1));
                speed = dtrans_q16_mul(speed, scale);
            }
        }
        speed_param = dtrans_q16_div(speed, spline->length);

        m->speed_param = speed_param;
        delta = (i64)speed_param * (i64)(q16_16)ticks;
        new_param = (i64)m->param + delta;

        if (speed_param >= 0) {
            if (new_param >= (i64)(q16_16)(1 << 16)) {
                m->param = (q16_16)(1 << 16);
                if (m->kind == D_MOVER_KIND_ITEM &&
                    spline->endpoint_b_eid != 0u &&
                    (spline->endpoint_b_port_kind == 0u ||
                     spline->endpoint_b_port_kind == (u16)D_STRUCT_PORT_ITEM_IN ||
                     spline->endpoint_b_port_kind == (u16)D_STRUCT_PORT_SPLINE_ITEM_IN)) {
                    d_struct_instance *dst = d_struct_get_mutable(w, (d_struct_instance_id)spline->endpoint_b_eid);
                    if (dst) {
                        d_container_state *c = (dst->inv_in.proto_id != 0u) ? &dst->inv_in : &dst->inv_out;
                        u32 packed = 0u;
                        if (c->proto_id != 0u && d_container_pack_items(c, (d_item_id)m->payload_id, m->payload_count, &packed) == 0 && packed == m->payload_count) {
                            consumed = 1;
                        }
                    }
                }
            } else {
                m->param = (q16_16)new_param;
            }
        } else {
            if (new_param <= 0) {
                m->param = 0;
                if (m->kind == D_MOVER_KIND_ITEM &&
                    spline->endpoint_a_eid != 0u &&
                    (spline->endpoint_a_port_kind == 0u ||
                     spline->endpoint_a_port_kind == (u16)D_STRUCT_PORT_ITEM_IN ||
                     spline->endpoint_a_port_kind == (u16)D_STRUCT_PORT_SPLINE_ITEM_IN)) {
                    d_struct_instance *dst = d_struct_get_mutable(w, (d_struct_instance_id)spline->endpoint_a_eid);
                    if (dst) {
                        d_container_state *c = (dst->inv_in.proto_id != 0u) ? &dst->inv_in : &dst->inv_out;
                        u32 packed = 0u;
                        if (c->proto_id != 0u && d_container_pack_items(c, (d_item_id)m->payload_id, m->payload_count, &packed) == 0 && packed == m->payload_count) {
                            consumed = 1;
                        }
                    }
                }
            } else {
                m->param = (q16_16)new_param;
            }
        }

        if (consumed) {
            st->movers[i] = st->movers[st->mover_count - 1u];
            st->mover_count -= 1u;
            continue;
        }

        m->param = dtrans_clamp_q16(m->param, 0, (q16_16)(1 << 16));
        i += 1u;
    }
}

void d_trans_tick(d_world *w, u32 ticks) {
    dtrans_world_state *st;
    u32 s;
    u32 t;
    const q16_16 spawn_gap = (q16_16)(1 << 13); /* 0.125 */

    if (!w || ticks == 0u) {
        return;
    }
    st = dtrans_find_world(w);
    if (!st) {
        return;
    }

    /* Spawn item movers from attached sources (best-effort, generic). */
    for (t = 0u; t < ticks; ++t) {
        for (s = 0u; s < st->spline_count; ++s) {
            d_spline_instance *sp = &st->splines[s];
            d_spline_profile_runtime prof;
            d_struct_instance *src;
            u32 mi;
            int blocked = 0;

            if (sp->endpoint_a_eid == 0u || sp->endpoint_b_eid == 0u) {
                continue;
            }
            if (sp->endpoint_a_port_kind != 0u &&
                sp->endpoint_a_port_kind != (u16)D_STRUCT_PORT_ITEM_OUT &&
                sp->endpoint_a_port_kind != (u16)D_STRUCT_PORT_SPLINE_ITEM_OUT) {
                continue;
            }
            if (d_trans_profile_resolve(w, sp->profile_id, &prof) != 0) {
                continue;
            }
            if (prof.type != (u16)D_SPLINE_TYPE_ITEM) {
                continue;
            }

            for (mi = 0u; mi < st->mover_count; ++mi) {
                if (st->movers[mi].spline_id == sp->id && st->movers[mi].param < spawn_gap) {
                    blocked = 1;
                    break;
                }
            }
            if (blocked) {
                continue;
            }

            src = d_struct_get_mutable(w, (d_struct_instance_id)sp->endpoint_a_eid);
            if (!src || src->inv_out.proto_id == 0u || !src->inv_out.slots) {
                continue;
            }

            {
                d_mover m;
                d_mover_id mid;
                d_item_id out_item = 0u;
                u32 unpacked = 0u;
                u32 sidx;
                u32 scount;
                memset(&m, 0, sizeof(m));
                m.kind = D_MOVER_KIND_ITEM;
                m.spline_id = sp->id;
                m.param = 0;
                m.speed_param = 0;
                m.size_param = spawn_gap;

                /* Deterministic: choose lowest item_id present in output container. */
                out_item = 0u;
                scount = (src->inv_out.slot_count > 0u) ? (u32)src->inv_out.slot_count : 1u;
                for (sidx = 0u; sidx < scount; ++sidx) {
                    if (src->inv_out.slots[sidx].item_id != 0u && src->inv_out.slots[sidx].count > 0u) {
                        if (out_item == 0u || src->inv_out.slots[sidx].item_id < out_item) {
                            out_item = src->inv_out.slots[sidx].item_id;
                        }
                    }
                }
                if (out_item == 0u) {
                    continue;
                }
                if (d_container_unpack_items(&src->inv_out, out_item, 1u, &unpacked) != 0 || unpacked != 1u) {
                    continue;
                }
                m.payload_id = (u32)out_item;
                m.payload_count = 1u;

                mid = d_trans_mover_create(w, &m);
                if (mid == 0u) {
                    /* Failed to spawn mover: return item to inventory. */
                    u32 packed = 0u;
                    (void)d_container_pack_items(&src->inv_out, out_item, 1u, &packed);
                }
            }
        }
    }

    d_trans_mover_tick(w, ticks);
}

static int dtrans_save_instance(d_world *w, d_tlv_blob *out) {
    dtrans_world_state *st;
    u32 i;
    u32 total;
    unsigned char *buf;
    unsigned char *dst;
    u32 version;

    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    if (!w) {
        return 0;
    }

    st = dtrans_find_world(w);
    if (!st || (st->spline_count == 0u && st->mover_count == 0u)) {
        return 0;
    }

    version = 3u;
    total = 0u;
    total += 4u; /* version */
    total += 4u; /* spline_count */
    for (i = 0u; i < st->spline_count; ++i) {
        const d_spline_instance *s = &st->splines[i];
        u16 ncount = s->node_count;
        total += sizeof(d_spline_id);
        total += sizeof(d_spline_profile_id);
        total += sizeof(d_org_id);
        total += sizeof(d_spline_flags);
        total += sizeof(u16); /* node_count */
        total += sizeof(u32); /* endpoint_a_eid */
        total += sizeof(u16) * 2u; /* endpoint_a_port_* */
        total += sizeof(u32); /* endpoint_b_eid */
        total += sizeof(u16) * 2u; /* endpoint_b_port_* */
        total += sizeof(q16_16); /* length */
        total += (u32)ncount * (sizeof(q32_32) * 3u + sizeof(q16_16) * 3u);
    }
    total += 4u; /* mover_count */
    total += st->mover_count * (
        sizeof(d_mover_id) +
        sizeof(u16) + sizeof(u16) +
        sizeof(d_spline_id) +
        sizeof(q16_16) * 3u +
        sizeof(u32) * 2u
    );

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &version, sizeof(u32)); dst += 4u;
    memcpy(dst, &st->spline_count, sizeof(u32)); dst += 4u;

    for (i = 0u; i < st->spline_count; ++i) {
        const d_spline_instance *s = &st->splines[i];
        u16 ncount = s->node_count;
        u16 n;
        memcpy(dst, &s->id, sizeof(d_spline_id)); dst += sizeof(d_spline_id);
        memcpy(dst, &s->profile_id, sizeof(d_spline_profile_id)); dst += sizeof(d_spline_profile_id);
        memcpy(dst, &s->owner_org, sizeof(d_org_id)); dst += sizeof(d_org_id);
        memcpy(dst, &s->flags, sizeof(d_spline_flags)); dst += sizeof(d_spline_flags);
        memcpy(dst, &ncount, sizeof(u16)); dst += sizeof(u16);
        memcpy(dst, &s->endpoint_a_eid, sizeof(u32)); dst += sizeof(u32);
        memcpy(dst, &s->endpoint_a_port_kind, sizeof(u16)); dst += sizeof(u16);
        memcpy(dst, &s->endpoint_a_port_index, sizeof(u16)); dst += sizeof(u16);
        memcpy(dst, &s->endpoint_b_eid, sizeof(u32)); dst += sizeof(u32);
        memcpy(dst, &s->endpoint_b_port_kind, sizeof(u16)); dst += sizeof(u16);
        memcpy(dst, &s->endpoint_b_port_index, sizeof(u16)); dst += sizeof(u16);
        memcpy(dst, &s->length, sizeof(q16_16)); dst += sizeof(q16_16);

        for (n = 0u; n < ncount; ++n) {
            const d_spline_node *sn = &st->nodes[(u32)s->node_start_index + (u32)n];
            memcpy(dst, &sn->x, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &sn->y, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &sn->z, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &sn->nx, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &sn->ny, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &sn->nz, sizeof(q16_16)); dst += sizeof(q16_16);
        }
    }

    memcpy(dst, &st->mover_count, sizeof(u32)); dst += 4u;
    for (i = 0u; i < st->mover_count; ++i) {
        const d_mover *m = &st->movers[i];
        u16 kind = (u16)m->kind;
        u16 pad = 0u;
        memcpy(dst, &m->id, sizeof(d_mover_id)); dst += sizeof(d_mover_id);
        memcpy(dst, &kind, sizeof(u16)); dst += sizeof(u16);
        memcpy(dst, &pad, sizeof(u16)); dst += sizeof(u16);
        memcpy(dst, &m->spline_id, sizeof(d_spline_id)); dst += sizeof(d_spline_id);
        memcpy(dst, &m->param, sizeof(q16_16)); dst += sizeof(q16_16);
        memcpy(dst, &m->speed_param, sizeof(q16_16)); dst += sizeof(q16_16);
        memcpy(dst, &m->size_param, sizeof(q16_16)); dst += sizeof(q16_16);
        memcpy(dst, &m->payload_id, sizeof(u32)); dst += sizeof(u32);
        memcpy(dst, &m->payload_count, sizeof(u32)); dst += sizeof(u32);
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int dtrans_load_instance(d_world *w, const d_tlv_blob *in) {
    dtrans_world_state *st;
    const unsigned char *ptr;
    u32 remaining;
    u32 version;
    u32 spline_count;
    u32 mover_count;
    u32 i;

    if (!w || !in) {
        return -1;
    }
    if (in->len == 0u) {
        return 0;
    }
    if (!in->ptr || in->len < 4u + 4u) {
        return -1;
    }

    st = dtrans_get_or_create_world(w);
    if (!st) {
        return -1;
    }
    (void)d_trans_init(w);

    ptr = in->ptr;
    remaining = in->len;
    memcpy(&version, ptr, sizeof(u32)); ptr += 4u; remaining -= 4u;
    if (version != 1u && version != 2u && version != 3u) {
        return -1;
    }
    memcpy(&spline_count, ptr, sizeof(u32)); ptr += 4u; remaining -= 4u;

    for (i = 0u; i < spline_count; ++i) {
        d_spline_id sid;
        d_spline_profile_id pid;
        d_org_id owner_org;
        d_spline_flags flags;
        u16 node_count;
        u32 endpoint_a_eid;
        u16 endpoint_a_kind;
        u16 endpoint_a_index;
        u32 endpoint_b_eid;
        u16 endpoint_b_kind;
        u16 endpoint_b_index;
        q16_16 length;
        d_spline_node *nodes;
        u32 n;
        u32 need;

        need = (u32)(sizeof(d_spline_id) + sizeof(d_spline_profile_id) + sizeof(d_spline_flags) + sizeof(u16) + sizeof(q16_16));
        if (version >= 3u) {
            need += (u32)sizeof(d_org_id);
        }
        if (remaining < need) {
            return -1;
        }
        memcpy(&sid, ptr, sizeof(d_spline_id)); ptr += sizeof(d_spline_id);
        memcpy(&pid, ptr, sizeof(d_spline_profile_id)); ptr += sizeof(d_spline_profile_id);
        owner_org = 0u;
        if (version >= 3u) {
            memcpy(&owner_org, ptr, sizeof(d_org_id)); ptr += sizeof(d_org_id);
            remaining -= (u32)sizeof(d_org_id);
        }
        memcpy(&flags, ptr, sizeof(d_spline_flags)); ptr += sizeof(d_spline_flags);
        memcpy(&node_count, ptr, sizeof(u16)); ptr += sizeof(u16);
        endpoint_a_eid = 0u;
        endpoint_a_kind = 0u;
        endpoint_a_index = 0u;
        endpoint_b_eid = 0u;
        endpoint_b_kind = 0u;
        endpoint_b_index = 0u;
        remaining -= (u32)(sizeof(d_spline_id) + sizeof(d_spline_profile_id) + sizeof(d_spline_flags) + sizeof(u16));
        if (version >= 2u) {
            if (remaining < sizeof(u32) + sizeof(u16) * 2u + sizeof(u32) + sizeof(u16) * 2u + sizeof(q16_16)) {
                return -1;
            }
            memcpy(&endpoint_a_eid, ptr, sizeof(u32)); ptr += sizeof(u32);
            memcpy(&endpoint_a_kind, ptr, sizeof(u16)); ptr += sizeof(u16);
            memcpy(&endpoint_a_index, ptr, sizeof(u16)); ptr += sizeof(u16);
            memcpy(&endpoint_b_eid, ptr, sizeof(u32)); ptr += sizeof(u32);
            memcpy(&endpoint_b_kind, ptr, sizeof(u16)); ptr += sizeof(u16);
            memcpy(&endpoint_b_index, ptr, sizeof(u16)); ptr += sizeof(u16);
            remaining -= (u32)(sizeof(u32) + sizeof(u16) * 2u + sizeof(u32) + sizeof(u16) * 2u);
        }
        memcpy(&length, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        remaining -= (u32)sizeof(q16_16);

        if (node_count < 2u) {
            return -1;
        }
        need = (u32)node_count * (sizeof(q32_32) * 3u + sizeof(q16_16) * 3u);
        if (remaining < need) {
            return -1;
        }
        nodes = (d_spline_node *)malloc(sizeof(d_spline_node) * (u32)node_count);
        if (!nodes) {
            return -1;
        }
        memset(nodes, 0, sizeof(d_spline_node) * (u32)node_count);
        for (n = 0u; n < (u32)node_count; ++n) {
            memcpy(&nodes[n].x, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
            memcpy(&nodes[n].y, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
            memcpy(&nodes[n].z, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
            memcpy(&nodes[n].nx, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
            memcpy(&nodes[n].ny, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
            memcpy(&nodes[n].nz, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        }
        remaining -= need;

        if (dtrans_spline_create_with_id(w, nodes, node_count, pid, flags, owner_org, sid) == 0u) {
            free(nodes);
            return -1;
        }
        /* Preserve cached length for determinism across profile changes. */
        {
            d_spline_instance *s = dtrans_find_spline(st, sid);
            if (s) {
                s->length = length;
                s->endpoint_a_eid = endpoint_a_eid;
                s->endpoint_a_port_kind = endpoint_a_kind;
                s->endpoint_a_port_index = endpoint_a_index;
                s->endpoint_b_eid = endpoint_b_eid;
                s->endpoint_b_port_kind = endpoint_b_kind;
                s->endpoint_b_port_index = endpoint_b_index;
            }
        }
        free(nodes);
    }

    if (remaining < 4u) {
        return -1;
    }
    memcpy(&mover_count, ptr, sizeof(u32)); ptr += 4u; remaining -= 4u;

    for (i = 0u; i < mover_count; ++i) {
        d_mover_id mid;
        u16 kind;
        u16 pad;
        d_spline_id spline_id;
        q16_16 param;
        q16_16 speed_param;
        q16_16 size_param;
        u32 payload_id;
        u32 payload_count;
        d_mover tmp;

        if (remaining < sizeof(d_mover_id) + sizeof(u16) * 2u + sizeof(d_spline_id) + sizeof(q16_16) * 3u + sizeof(u32) * 2u) {
            return -1;
        }
        memcpy(&mid, ptr, sizeof(d_mover_id)); ptr += sizeof(d_mover_id);
        memcpy(&kind, ptr, sizeof(u16)); ptr += sizeof(u16);
        memcpy(&pad, ptr, sizeof(u16)); ptr += sizeof(u16);
        (void)pad;
        memcpy(&spline_id, ptr, sizeof(d_spline_id)); ptr += sizeof(d_spline_id);
        memcpy(&param, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&speed_param, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&size_param, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&payload_id, ptr, sizeof(u32)); ptr += sizeof(u32);
        memcpy(&payload_count, ptr, sizeof(u32)); ptr += sizeof(u32);
        remaining -= (u32)(sizeof(d_mover_id) + sizeof(u16) * 2u + sizeof(d_spline_id) + sizeof(q16_16) * 3u + sizeof(u32) * 2u);

        memset(&tmp, 0, sizeof(tmp));
        tmp.id = mid;
        tmp.kind = (d_mover_kind)kind;
        tmp.spline_id = spline_id;
        tmp.param = param;
        tmp.speed_param = speed_param;
        tmp.size_param = size_param;
        tmp.payload_id = payload_id;
        tmp.payload_count = payload_count;

        if (dtrans_mover_create_with_id(w, &tmp, mid) == 0u) {
            return -1;
        }
    }

    return 0;
}

static int dtrans_save_chunk(d_world *w, d_chunk *chunk, d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int dtrans_load_chunk(d_world *w, d_chunk *chunk, const d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static void dtrans_init_instance_subsys(d_world *w) {
    (void)d_trans_init(w);
}

static void dtrans_tick_subsys(d_world *w, u32 ticks) {
    d_trans_tick(w, ticks);
}

static void dtrans_register_models(void) {
    /* Future: register transport models, if needed. */
}

static void dtrans_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_trans_subsystem = {
    D_SUBSYS_TRANS,
    "trans",
    2u,
    dtrans_register_models,
    dtrans_load_protos,
    dtrans_init_instance_subsys,
    dtrans_tick_subsys,
    dtrans_save_chunk,
    dtrans_load_chunk,
    dtrans_save_instance,
    dtrans_load_instance
};

void d_trans_register_subsystem(void) {
    if (g_trans_registered) {
        return;
    }
    if (d_subsystem_register(&g_trans_subsystem) == 0) {
        g_trans_registered = 1;
    }
}
