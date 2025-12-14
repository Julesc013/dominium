/* DECOR deterministic compilation pipeline (C89). */
#include "decor/compile/dg_decor_compile.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "core/dg_det_hash.h"
#include "core/dg_order_key.h"
#include "core/dg_quant.h"
#include "domino/core/rng.h"
#include "res/dg_tlv_canon.h"
#include "sim/sched/dg_phase.h"

static dg_q dg_q_min(dg_q a, dg_q b) { return (a < b) ? a : b; }
static dg_q dg_q_max(dg_q a, dg_q b) { return (a > b) ? a : b; }

static void canon_range(dg_q *a0, dg_q *a1) {
    dg_q lo;
    dg_q hi;
    if (!a0 || !a1) return;
    lo = dg_q_min(*a0, *a1);
    hi = dg_q_max(*a0, *a1);
    *a0 = lo;
    *a1 = hi;
}

static u64 hash_bytes(u64 h, const unsigned char *p, u32 n) {
    u32 i;
    if (!p) return dg_det_hash_u64(h ^ 0xBADC0FFEE0DDF00DULL);
    for (i = 0u; i < n; ++i) {
        h = dg_det_hash_u64(h ^ (u64)p[i]);
    }
    return h;
}

static u64 hash_tlv(u64 h, const unsigned char *tlv, u32 tlv_len) {
    unsigned char tmp[256];
    u32 tmp_len = 0u;
    if (!tlv || tlv_len == 0u) return dg_det_hash_u64(h ^ 0u);
    if (tlv_len <= (u32)sizeof(tmp)) {
        if (dg_tlv_canon(tlv, tlv_len, tmp, (u32)sizeof(tmp), &tmp_len) == 0) {
            return hash_bytes(h, tmp, tmp_len);
        }
    }
    h = dg_det_hash_u64(h ^ (u64)tlv_len);
    return hash_bytes(h, tlv, tlv_len);
}

static u64 hash_anchor(u64 h, const dg_anchor *a) {
    if (!a) return dg_det_hash_u64(h ^ 0u);
    h = dg_det_hash_u64(h ^ (u64)a->kind);
    h = dg_det_hash_u64(h ^ (u64)a->host_frame);
    switch (a->kind) {
    case DG_ANCHOR_TERRAIN:
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.terrain.u);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.terrain.v);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.terrain.h);
        break;
    case DG_ANCHOR_CORRIDOR_TRANS:
        h = dg_det_hash_u64(h ^ (u64)a->u.corridor.alignment_id);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.corridor.s);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.corridor.t);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.corridor.h);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.corridor.roll);
        break;
    case DG_ANCHOR_STRUCT_SURFACE:
        h = dg_det_hash_u64(h ^ (u64)a->u.struct_surface.structure_id);
        h = dg_det_hash_u64(h ^ (u64)a->u.struct_surface.surface_id);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.struct_surface.u);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.struct_surface.v);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.struct_surface.offset);
        break;
    case DG_ANCHOR_ROOM_SURFACE:
        h = dg_det_hash_u64(h ^ (u64)a->u.room_surface.room_id);
        h = dg_det_hash_u64(h ^ (u64)a->u.room_surface.surface_id);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.room_surface.u);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.room_surface.v);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.room_surface.offset);
        break;
    case DG_ANCHOR_SOCKET:
        h = dg_det_hash_u64(h ^ (u64)a->u.socket.socket_id);
        h = dg_det_hash_u64(h ^ (u64)(i64)a->u.socket.param);
        break;
    default:
        break;
    }
    return h;
}

static u64 hash_pose(u64 h, const dg_pose *p) {
    if (!p) return dg_det_hash_u64(h ^ 0u);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->pos.x);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->pos.y);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->pos.z);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->rot.x);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->rot.y);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->rot.z);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->rot.w);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->incline);
    h = dg_det_hash_u64(h ^ (u64)(i64)p->roll);
    return h;
}

static u64 hash_host_desc(const dg_decor_host_desc *d) {
    u64 h = 0xDEC0D0C0A5515EEDULL;
    if (!d) return 0u;
    h = dg_det_hash_u64(h ^ dg_decor_host_stable_id_u64(&d->host));
    h = dg_det_hash_u64(h ^ (u64)d->chunk_id);
    h = dg_det_hash_u64(h ^ (u64)d->host_frame);
    h = dg_det_hash_u64(h ^ (u64)(i64)d->primary0);
    h = dg_det_hash_u64(h ^ (u64)(i64)d->primary1);
    h = dg_det_hash_u64(h ^ (u64)(i64)d->secondary0);
    h = dg_det_hash_u64(h ^ (u64)(i64)d->secondary1);
    return h;
}

static u32 host_lower_bound(const dg_decor_compiler *c, const dg_decor_host *host) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;
    if (!c || !host) return 0u;
    hi = c->host_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_decor_host_cmp(&c->hosts[mid].desc.host, host);
        if (cmp >= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 chunk_lower_bound(const dg_decor_compiler *c, dg_chunk_id chunk_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!c) return 0u;
    hi = c->chunk_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (c->chunks[mid].chunk_id >= chunk_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 rulepack_state_lower_bound(const dg_decor_compiler *c, dg_decor_rulepack_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!c) return 0u;
    hi = c->rulepack_state_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (c->rulepack_state[mid].id >= id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int reserve_hosts(dg_decor_compiler *c, u32 capacity) {
    dg_decor_compiled_host *arr;
    u32 new_cap;
    if (!c) return -1;
    if (capacity <= c->host_capacity) return 0;
    new_cap = c->host_capacity ? c->host_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_compiled_host *)realloc(c->hosts, sizeof(dg_decor_compiled_host) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > c->host_capacity) {
        memset(&arr[c->host_capacity], 0, sizeof(dg_decor_compiled_host) * (size_t)(new_cap - c->host_capacity));
    }
    c->hosts = arr;
    c->host_capacity = new_cap;
    return 0;
}

static int reserve_chunks(dg_decor_compiler *c, u32 capacity) {
    dg_decor_compiled_chunk *arr;
    u32 new_cap;
    if (!c) return -1;
    if (capacity <= c->chunk_capacity) return 0;
    new_cap = c->chunk_capacity ? c->chunk_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_compiled_chunk *)realloc(c->chunks, sizeof(dg_decor_compiled_chunk) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > c->chunk_capacity) {
        memset(&arr[c->chunk_capacity], 0, sizeof(dg_decor_compiled_chunk) * (size_t)(new_cap - c->chunk_capacity));
    }
    c->chunks = arr;
    c->chunk_capacity = new_cap;
    return 0;
}

static int reserve_rulepack_ptrs(dg_decor_compiler *c, u32 capacity) {
    const dg_decor_rulepack **arr;
    u32 new_cap;
    if (!c) return -1;
    if (capacity <= c->rulepack_capacity) return 0;
    new_cap = c->rulepack_capacity ? c->rulepack_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (const dg_decor_rulepack **)realloc(c->rulepacks, sizeof(*arr) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > c->rulepack_capacity) {
        memset(&arr[c->rulepack_capacity], 0, sizeof(*arr) * (size_t)(new_cap - c->rulepack_capacity));
    }
    c->rulepacks = arr;
    c->rulepack_capacity = new_cap;
    return 0;
}

static int reserve_override_ptrs(dg_decor_compiler *c, u32 capacity) {
    const dg_decor_override **arr;
    u32 new_cap;
    if (!c) return -1;
    if (capacity <= c->override_capacity) return 0;
    new_cap = c->override_capacity ? c->override_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (const dg_decor_override **)realloc(c->overrides, sizeof(*arr) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > c->override_capacity) {
        memset(&arr[c->override_capacity], 0, sizeof(*arr) * (size_t)(new_cap - c->override_capacity));
    }
    c->overrides = arr;
    c->override_capacity = new_cap;
    return 0;
}

static int reserve_rulepack_state(dg_decor_compiler *c, u32 capacity) {
    dg_decor_rulepack_state *arr;
    u32 new_cap;
    if (!c) return -1;
    if (capacity <= c->rulepack_state_capacity) return 0;
    new_cap = c->rulepack_state_capacity ? c->rulepack_state_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_rulepack_state *)realloc(c->rulepack_state, sizeof(dg_decor_rulepack_state) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > c->rulepack_state_capacity) {
        memset(&arr[c->rulepack_state_capacity], 0, sizeof(dg_decor_rulepack_state) * (size_t)(new_cap - c->rulepack_state_capacity));
    }
    c->rulepack_state = arr;
    c->rulepack_state_capacity = new_cap;
    return 0;
}

static int cmp_rulepack_ptr(const void *pa, const void *pb) {
    const dg_decor_rulepack *a = *(const dg_decor_rulepack * const *)pa;
    const dg_decor_rulepack *b = *(const dg_decor_rulepack * const *)pb;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP_U64(a->id, b->id);
}

static int cmp_override_ptr(const void *pa, const void *pb) {
    const dg_decor_override *a = *(const dg_decor_override * const *)pa;
    const dg_decor_override *b = *(const dg_decor_override * const *)pb;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP_U64(a->id, b->id);
}

static int cmp_host_desc(const void *pa, const void *pb) {
    const dg_decor_host_desc *a = (const dg_decor_host_desc *)pa;
    const dg_decor_host_desc *b = (const dg_decor_host_desc *)pb;
    int c;
    c = dg_decor_host_cmp(&a->host, &b->host);
    if (c) return c;
    c = D_DET_CMP_U64((u64)a->chunk_id, (u64)b->chunk_id);
    if (c) return c;
    c = D_DET_CMP_U64((u64)a->host_frame, (u64)b->host_frame);
    if (c) return c;
    c = D_DET_CMP_I64((i64)a->primary0, (i64)b->primary0);
    if (c) return c;
    c = D_DET_CMP_I64((i64)a->primary1, (i64)b->primary1);
    if (c) return c;
    c = D_DET_CMP_I64((i64)a->secondary0, (i64)b->secondary0);
    if (c) return c;
    c = D_DET_CMP_I64((i64)a->secondary1, (i64)b->secondary1);
    if (c) return c;
    return 0;
}

static int cmp_item_qsort(const void *pa, const void *pb) {
    const dg_decor_item *a = (const dg_decor_item *)pa;
    const dg_decor_item *b = (const dg_decor_item *)pb;
    return dg_decor_item_cmp(a, b);
}

static int host_items_reserve(dg_decor_compiled_host *h, u32 capacity) {
    dg_decor_item *arr;
    u32 new_cap;
    if (!h) return -1;
    if (capacity <= h->item_capacity) return 0;
    new_cap = h->item_capacity ? h->item_capacity : 16u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_item *)realloc(h->items, sizeof(dg_decor_item) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > h->item_capacity) {
        memset(&arr[h->item_capacity], 0, sizeof(dg_decor_item) * (size_t)(new_cap - h->item_capacity));
    }
    h->items = arr;
    h->item_capacity = new_cap;
    return 0;
}

static int host_items_push(dg_decor_compiled_host *h, const dg_decor_item *it) {
    if (!h || !it) return -1;
    if (host_items_reserve(h, h->item_count + 1u) != 0) return -2;
    h->items[h->item_count++] = *it;
    return 0;
}

static void host_items_remove_at(dg_decor_compiled_host *h, u32 idx) {
    if (!h) return;
    if (idx >= h->item_count) return;
    if (idx + 1u < h->item_count) {
        memmove(&h->items[idx], &h->items[idx + 1u], sizeof(dg_decor_item) * (size_t)(h->item_count - idx - 1u));
    }
    h->item_count -= 1u;
}

static int host_find_decor_id(const dg_decor_compiled_host *h, dg_decor_id id) {
    u32 i;
    if (!h || id == 0u) return -1;
    for (i = 0u; i < h->item_count; ++i) {
        if (h->items[i].decor_id == id) return (int)i;
    }
    return -1;
}

static void quantize_anchor(dg_anchor *a) {
    if (!a) return;
    switch (a->kind) {
    case DG_ANCHOR_TERRAIN:
        a->u.terrain.u = dg_quant_param(a->u.terrain.u, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.terrain.v = dg_quant_param(a->u.terrain.v, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.terrain.h = dg_quant_pos(a->u.terrain.h, DG_QUANT_POS_DEFAULT_Q);
        break;
    case DG_ANCHOR_CORRIDOR_TRANS:
        a->u.corridor.s = dg_quant_param(a->u.corridor.s, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.corridor.t = dg_quant_param(a->u.corridor.t, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.corridor.h = dg_quant_pos(a->u.corridor.h, DG_QUANT_POS_DEFAULT_Q);
        a->u.corridor.roll = dg_quant_angle(a->u.corridor.roll, DG_QUANT_ANGLE_DEFAULT_Q);
        break;
    case DG_ANCHOR_STRUCT_SURFACE:
        a->u.struct_surface.u = dg_quant_param(a->u.struct_surface.u, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.struct_surface.v = dg_quant_param(a->u.struct_surface.v, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.struct_surface.offset = dg_quant_pos(a->u.struct_surface.offset, DG_QUANT_POS_DEFAULT_Q);
        break;
    case DG_ANCHOR_ROOM_SURFACE:
        a->u.room_surface.u = dg_quant_param(a->u.room_surface.u, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.room_surface.v = dg_quant_param(a->u.room_surface.v, DG_QUANT_PARAM_DEFAULT_Q);
        a->u.room_surface.offset = dg_quant_pos(a->u.room_surface.offset, DG_QUANT_POS_DEFAULT_Q);
        break;
    case DG_ANCHOR_SOCKET:
        a->u.socket.param = dg_quant_param(a->u.socket.param, DG_QUANT_PARAM_DEFAULT_Q);
        break;
    default:
        break;
    }
}

static void quantize_pose(dg_pose *p) {
    if (!p) return;
    p->pos.x = dg_quant_pos(p->pos.x, DG_QUANT_POS_DEFAULT_Q);
    p->pos.y = dg_quant_pos(p->pos.y, DG_QUANT_POS_DEFAULT_Q);
    p->pos.z = dg_quant_pos(p->pos.z, DG_QUANT_POS_DEFAULT_Q);
    p->incline = dg_quant_angle(p->incline, DG_QUANT_ANGLE_DEFAULT_Q);
    p->roll = dg_quant_angle(p->roll, DG_QUANT_ANGLE_DEFAULT_Q);
}

static dg_anchor_kind anchor_kind_for_host(dg_decor_host_kind hk) {
    switch (hk) {
    case DG_DECOR_HOST_TERRAIN_PATCH: return DG_ANCHOR_TERRAIN;
    case DG_DECOR_HOST_TRANS_SLOT_SURFACE: return DG_ANCHOR_CORRIDOR_TRANS;
    case DG_DECOR_HOST_STRUCT_SURFACE: return DG_ANCHOR_STRUCT_SURFACE;
    case DG_DECOR_HOST_ROOM_SURFACE: return DG_ANCHOR_ROOM_SURFACE;
    case DG_DECOR_HOST_SOCKET: return DG_ANCHOR_SOCKET;
    default: return DG_ANCHOR_NONE;
    }
}

static void build_anchor_for_host(
    dg_anchor               *out_anchor,
    const dg_decor_host_desc *hd,
    dg_q                    primary,
    dg_q                    secondary
) {
    dg_anchor a;
    dg_anchor_clear(&a);
    if (!out_anchor || !hd) return;

    a.kind = anchor_kind_for_host(hd->host.kind);
    a._pad32 = 0u;
    a.host_frame = hd->host_frame;

    switch (hd->host.kind) {
    case DG_DECOR_HOST_TERRAIN_PATCH:
        a.u.terrain.u = primary;
        a.u.terrain.v = secondary;
        a.u.terrain.h = 0;
        break;
    case DG_DECOR_HOST_TRANS_SLOT_SURFACE:
        a.u.corridor.alignment_id = hd->host.u.trans_slot_surface.alignment_id;
        a.u.corridor.s = primary;
        a.u.corridor.t = 0;
        a.u.corridor.h = 0;
        a.u.corridor.roll = 0;
        break;
    case DG_DECOR_HOST_STRUCT_SURFACE:
        a.u.struct_surface.structure_id = hd->host.u.struct_surface.struct_id;
        a.u.struct_surface.surface_id = hd->host.u.struct_surface.surface_id;
        a.u.struct_surface.u = primary;
        a.u.struct_surface.v = secondary;
        a.u.struct_surface.offset = 0;
        break;
    case DG_DECOR_HOST_ROOM_SURFACE:
        a.u.room_surface.room_id = hd->host.u.room_surface.room_id;
        a.u.room_surface.surface_id = hd->host.u.room_surface.surface_id;
        a.u.room_surface.u = primary;
        a.u.room_surface.v = secondary;
        a.u.room_surface.offset = 0;
        break;
    case DG_DECOR_HOST_SOCKET:
        a.u.socket.socket_id = hd->host.u.socket.socket_id;
        a.u.socket.param = primary;
        break;
    default:
        break;
    }

    quantize_anchor(&a);
    *out_anchor = a;
}

static u32 seed_from_u64(u64 v) { return (u32)(v ^ (v >> 32)); }

static u64 make_decor_id(
    u64                     global_seed,
    const dg_decor_host_desc *hd,
    dg_decor_rulepack_id     rulepack_id,
    dg_decor_type_id         type_id,
    u32                      index
) {
    u64 h;
    if (!hd) return 0u;
    h = dg_det_hash_u64(global_seed ^ dg_decor_host_stable_id_u64(&hd->host) ^ (u64)rulepack_id);
    h = dg_det_hash_u64(h ^ (u64)type_id);
    h = dg_det_hash_u64(h ^ (u64)index);
    return h;
}

static void generate_baseline_for_host(dg_decor_compiler *c, dg_decor_compiled_host *h) {
    u32 rpi;
    if (!c || !h) return;

    h->item_count = 0u;

    for (rpi = 0u; rpi < c->rulepack_count; ++rpi) {
        const dg_decor_rulepack *rp = c->rulepacks[rpi];
        d_rng_state rng;
        dg_q p0;
        dg_q p1;
        dg_q interval;
        dg_q pos;
        dg_q secondary_mid;
        u32 pos_index;
        u64 seed64;
        u32 jitter_raw;
        dg_q jitter_q;
        u32 spi;

        if (!rp) continue;
        if (rp->id == 0u) continue;
        if (!dg_decor_rulepack_matches_host(rp, &h->desc.host)) continue;

        p0 = h->desc.primary0;
        p1 = h->desc.primary1;
        interval = rp->interval_q;

        secondary_mid = (dg_q)(((i64)h->desc.secondary0 + (i64)h->desc.secondary1) / 2);

        seed64 = dg_det_hash_u64(c->global_seed ^ dg_decor_host_stable_id_u64(&h->desc.host) ^ (u64)rp->id);
        d_rng_seed(&rng, seed_from_u64(seed64));
        jitter_raw = d_rng_next_u32(&rng);

        jitter_q = 0;
        if (interval > 0) {
            u64 interval_raw = (u64)(i64)interval;
            if (interval_raw != 0u) {
                jitter_q = (dg_q)(i64)((u64)jitter_raw % interval_raw);
            }
        }

        pos = (dg_q)d_q48_16_add((q48_16)p0, (q48_16)rp->start_q);
        pos = (dg_q)d_q48_16_add((q48_16)pos, (q48_16)jitter_q);
        pos_index = 0u;

        if (interval <= 0) {
            dg_decor_item it;
            dg_q clamped = D_CLAMP(pos, p0, p1);
            for (spi = 0u; spi < rp->spawn_count; ++spi) {
                const dg_decor_spawn_template *st = &rp->spawns[spi];
                dg_decor_item_clear(&it);
                it.decor_type_id = st->decor_type_id;
                it.decor_id = (dg_decor_id)make_decor_id(c->global_seed, &h->desc, rp->id, st->decor_type_id, pos_index);
                it.flags = st->flags;
                it._pad32 = 0u;
                it.host = h->desc.host;
                it.local_offset = st->local_offset;
                quantize_pose(&it.local_offset);
                it.params = st->params;
                build_anchor_for_host(&it.anchor, &h->desc, clamped, secondary_mid);
                (void)host_items_push(h, &it);
            }
            continue;
        }

        /* Advance to the first position within [p0, p1]. */
        while (pos < p0) {
            pos = (dg_q)d_q48_16_add((q48_16)pos, (q48_16)interval);
            pos_index += 1u;
        }

        while (pos <= p1) {
            dg_decor_item it;
            for (spi = 0u; spi < rp->spawn_count; ++spi) {
                const dg_decor_spawn_template *st = &rp->spawns[spi];
                dg_decor_item_clear(&it);
                it.decor_type_id = st->decor_type_id;
                it.decor_id = (dg_decor_id)make_decor_id(c->global_seed, &h->desc, rp->id, st->decor_type_id, pos_index);
                it.flags = st->flags;
                it._pad32 = 0u;
                it.host = h->desc.host;
                it.local_offset = st->local_offset;
                quantize_pose(&it.local_offset);
                it.params = st->params;
                build_anchor_for_host(&it.anchor, &h->desc, pos, secondary_mid);
                (void)host_items_push(h, &it);
            }
            pos = (dg_q)d_q48_16_add((q48_16)pos, (q48_16)interval);
            pos_index += 1u;
        }
    }
}

static void apply_overrides_for_host(dg_decor_compiler *c, dg_decor_compiled_host *h) {
    u32 oi;
    if (!c || !h) return;

    /* Apply PIN snapshots first so subsequent overrides can target them regardless of ordering. */
    for (oi = 0u; oi < c->override_count; ++oi) {
        const dg_decor_override *ovr = c->overrides[oi];
        dg_decor_item pin;
        int idx;
        if (!ovr) continue;
        if (ovr->op != DG_DECOR_OVERRIDE_PIN) continue;
        pin = ovr->u.pin.item;
        if (pin.decor_id == 0u) continue;
        if (dg_decor_host_cmp(&pin.host, &h->desc.host) != 0) continue;

        pin.flags |= DG_DECOR_ITEM_F_PINNED;
        pin.host = h->desc.host;
        pin.anchor.host_frame = h->desc.host_frame;
        pin.anchor.kind = anchor_kind_for_host(h->desc.host.kind);
        quantize_anchor(&pin.anchor);
        quantize_pose(&pin.local_offset);

        idx = host_find_decor_id(h, pin.decor_id);
        if (idx >= 0) {
            h->items[(u32)idx] = pin;
        } else {
            (void)host_items_push(h, &pin);
        }
    }

    for (oi = 0u; oi < c->override_count; ++oi) {
        const dg_decor_override *ovr = c->overrides[oi];
        if (!ovr) continue;

        if (ovr->op == DG_DECOR_OVERRIDE_SUPPRESS) {
            dg_decor_suppress_region region = ovr->u.suppress.region;
            u32 i;
            dg_decor_suppress_region_canon(&region);
            if (dg_decor_host_cmp(&region.host, &h->desc.host) != 0) continue;
            for (i = 0u; i < h->item_count; /* manual */) {
                const dg_decor_item *it = &h->items[i];
                if ((it->flags & DG_DECOR_ITEM_F_PINNED) != 0u) {
                    i += 1u;
                    continue;
                }
                if (dg_decor_suppress_region_contains_anchor(&region, &it->anchor)) {
                    host_items_remove_at(h, i);
                    continue;
                }
                i += 1u;
            }
            continue;
        }

        if (ovr->op == DG_DECOR_OVERRIDE_REPLACE) {
            const dg_decor_override_replace *r = &ovr->u.replace;
            int idx = host_find_decor_id(h, r->target_decor_id);
            if (idx >= 0) {
                dg_decor_item *it = &h->items[(u32)idx];
                if (r->new_decor_type_id != 0u) it->decor_type_id = r->new_decor_type_id;
                if (r->new_params.len != 0u) it->params = r->new_params;
                it->flags = (it->flags & ~r->new_flags_mask) | (r->new_flags_value & r->new_flags_mask);
            }
            continue;
        }

        if (ovr->op == DG_DECOR_OVERRIDE_MOVE) {
            const dg_decor_override_move *m = &ovr->u.move;
            int idx = host_find_decor_id(h, m->target_decor_id);
            if (idx >= 0) {
                dg_decor_item *it = &h->items[(u32)idx];
                if (m->has_anchor) {
                    it->anchor = m->new_anchor;
                    it->anchor.host_frame = h->desc.host_frame;
                    it->anchor.kind = anchor_kind_for_host(h->desc.host.kind);
                    quantize_anchor(&it->anchor);
                }
                if (m->has_local_offset) {
                    it->local_offset = m->new_local_offset;
                    quantize_pose(&it->local_offset);
                }
            }
            continue;
        }

        if (ovr->op == DG_DECOR_OVERRIDE_TAG) {
            /* TAG is metadata-only in this prompt; no compiled output changes. */
            continue;
        }
    }

    /* Canonicalize final item order for this host. */
    if (h->item_count > 1u) {
        qsort(h->items, (size_t)h->item_count, sizeof(dg_decor_item), cmp_item_qsort);
    }
}

static dg_decor_compiled_chunk *get_or_add_chunk(dg_decor_compiler *c, dg_chunk_id chunk_id) {
    u32 idx;
    if (!c || chunk_id == 0u) return (dg_decor_compiled_chunk *)0;
    idx = chunk_lower_bound(c, chunk_id);
    if (idx < c->chunk_count && c->chunks[idx].chunk_id == chunk_id) {
        return &c->chunks[idx];
    }
    if (reserve_chunks(c, c->chunk_count + 1u) != 0) return (dg_decor_compiled_chunk *)0;
    if (idx < c->chunk_count) {
        memmove(&c->chunks[idx + 1u], &c->chunks[idx],
                sizeof(dg_decor_compiled_chunk) * (size_t)(c->chunk_count - idx));
    }
    memset(&c->chunks[idx], 0, sizeof(c->chunks[idx]));
    c->chunks[idx].chunk_id = chunk_id;
    c->chunks[idx].present = D_TRUE;
    dg_decor_instances_init(&c->chunks[idx].instances);
    dg_decor_tiles_init(&c->chunks[idx].tiles);
    c->chunk_count += 1u;
    return &c->chunks[idx];
}

static dg_decor_compiled_host *get_or_add_host(dg_decor_compiler *c, const dg_decor_host_desc *desc, d_bool *out_added) {
    u32 idx;
    if (out_added) *out_added = D_FALSE;
    if (!c || !desc) return (dg_decor_compiled_host *)0;
    idx = host_lower_bound(c, &desc->host);
    if (idx < c->host_count && dg_decor_host_cmp(&c->hosts[idx].desc.host, &desc->host) == 0) {
        return &c->hosts[idx];
    }
    if (reserve_hosts(c, c->host_count + 1u) != 0) return (dg_decor_compiled_host *)0;
    if (idx < c->host_count) {
        memmove(&c->hosts[idx + 1u], &c->hosts[idx],
                sizeof(dg_decor_compiled_host) * (size_t)(c->host_count - idx));
    }
    memset(&c->hosts[idx], 0, sizeof(c->hosts[idx]));
    c->hosts[idx].desc = *desc;
    c->hosts[idx].desc_hash = hash_host_desc(desc);
    c->hosts[idx].present = D_TRUE;
    c->hosts[idx].items = (dg_decor_item *)0;
    c->hosts[idx].item_count = 0u;
    c->hosts[idx].item_capacity = 0u;
    c->host_count += 1u;
    if (out_added) *out_added = D_TRUE;
    return &c->hosts[idx];
}

static u64 hash_overrides_sorted(const dg_decor_compiler *c) {
    u64 h = 0x0AEA1DEDEC0F00DULL;
    u32 i;
    if (!c) return 0u;
    h = dg_det_hash_u64(h ^ (u64)c->override_count);
    for (i = 0u; i < c->override_count; ++i) {
        const dg_decor_override *o = c->overrides[i];
        if (!o) continue;
        h = dg_det_hash_u64(h ^ (u64)o->id);
        h = dg_det_hash_u64(h ^ (u64)o->op);
        switch (o->op) {
        case DG_DECOR_OVERRIDE_PIN: {
            const dg_decor_item *it = &o->u.pin.item;
            h = dg_det_hash_u64(h ^ (u64)it->decor_id);
            h = dg_det_hash_u64(h ^ (u64)it->decor_type_id);
            h = dg_det_hash_u64(h ^ (u64)it->flags);
            h = dg_det_hash_u64(h ^ dg_decor_host_stable_id_u64(&it->host));
            h = hash_anchor(h, &it->anchor);
            h = hash_pose(h, &it->local_offset);
            h = hash_tlv(h, it->params.ptr, it->params.len);
        } break;
        case DG_DECOR_OVERRIDE_SUPPRESS: {
            const dg_decor_suppress_region *r = &o->u.suppress.region;
            h = dg_det_hash_u64(h ^ dg_decor_host_stable_id_u64(&r->host));
            h = dg_det_hash_u64(h ^ (u64)(i64)r->u0);
            h = dg_det_hash_u64(h ^ (u64)(i64)r->u1);
            h = dg_det_hash_u64(h ^ (u64)(i64)r->v0);
            h = dg_det_hash_u64(h ^ (u64)(i64)r->v1);
            h = dg_det_hash_u64(h ^ (u64)(i64)r->s0);
            h = dg_det_hash_u64(h ^ (u64)(i64)r->s1);
            h = dg_det_hash_u64(h ^ (u64)(i64)r->param0);
            h = dg_det_hash_u64(h ^ (u64)(i64)r->param1);
        } break;
        case DG_DECOR_OVERRIDE_REPLACE: {
            const dg_decor_override_replace *r = &o->u.replace;
            h = dg_det_hash_u64(h ^ (u64)r->target_decor_id);
            h = dg_det_hash_u64(h ^ (u64)r->new_decor_type_id);
            h = dg_det_hash_u64(h ^ (u64)r->new_flags_mask);
            h = dg_det_hash_u64(h ^ (u64)r->new_flags_value);
            h = hash_tlv(h, r->new_params.ptr, r->new_params.len);
        } break;
        case DG_DECOR_OVERRIDE_MOVE: {
            const dg_decor_override_move *m = &o->u.move;
            h = dg_det_hash_u64(h ^ (u64)m->target_decor_id);
            h = dg_det_hash_u64(h ^ (u64)m->has_anchor);
            h = dg_det_hash_u64(h ^ (u64)m->has_local_offset);
            h = hash_anchor(h, &m->new_anchor);
            h = hash_pose(h, &m->new_local_offset);
        } break;
        case DG_DECOR_OVERRIDE_TAG: {
            const dg_decor_override_tag *t = &o->u.tag;
            h = dg_det_hash_u64(h ^ (u64)t->target_decor_id);
            h = dg_det_hash_u64(h ^ (u64)t->tag_id);
            h = dg_det_hash_u64(h ^ (u64)t->value);
        } break;
        default:
            break;
        }
    }
    return h;
}

void dg_decor_compiler_init(dg_decor_compiler *c) {
    if (!c) return;
    memset(c, 0, sizeof(*c));
    dg_decor_dirty_init(&c->dirty);
    dg_work_queue_init(&c->work_q);
}

void dg_decor_compiler_free(dg_decor_compiler *c) {
    u32 i;
    if (!c) return;

    if (c->hosts) {
        for (i = 0u; i < c->host_count; ++i) {
            if (c->hosts[i].items) free(c->hosts[i].items);
            memset(&c->hosts[i], 0, sizeof(c->hosts[i]));
        }
        free(c->hosts);
    }

    if (c->chunks) {
        for (i = 0u; i < c->chunk_count; ++i) {
            dg_decor_instances_free(&c->chunks[i].instances);
            dg_decor_tiles_free(&c->chunks[i].tiles);
            memset(&c->chunks[i], 0, sizeof(c->chunks[i]));
        }
        free(c->chunks);
    }

    if (c->rulepacks) free(c->rulepacks);
    if (c->overrides) free(c->overrides);
    if (c->rulepack_state) free(c->rulepack_state);

    dg_decor_dirty_free(&c->dirty);
    dg_work_queue_free(&c->work_q);
    dg_decor_compiler_init(c);
}

int dg_decor_compiler_reserve(dg_decor_compiler *c, u32 work_queue_capacity) {
    if (!c) return -1;
    if (dg_work_queue_reserve(&c->work_q, work_queue_capacity) != 0) return -2;
    return 0;
}

int dg_decor_compiler_sync(dg_decor_compiler *c, const dg_decor_compile_input *in) {
    dg_decor_host_desc *tmp_hosts;
    u32 i;
    u32 removed_rulepacks;
    d_bool seed_changed;

    if (!c || !in) return -1;

    seed_changed = (c->global_seed != in->global_seed) ? D_TRUE : D_FALSE;
    c->global_seed = in->global_seed;

    /* Canonicalize rulepack pointer list by id. */
    if (reserve_rulepack_ptrs(c, in->rulepack_count) != 0) return -2;
    c->rulepack_count = in->rulepack_count;
    for (i = 0u; i < in->rulepack_count; ++i) {
        c->rulepacks[i] = &in->rulepacks[i];
    }
    if (c->rulepack_count > 1u) {
        qsort(c->rulepacks, (size_t)c->rulepack_count, sizeof(c->rulepacks[0]), cmp_rulepack_ptr);
    }

    /* Update rulepack state hashes (mark dirty on content change). */
    for (i = 0u; i < c->rulepack_state_count; ++i) {
        c->rulepack_state[i].present = D_FALSE;
    }

    for (i = 0u; i < c->rulepack_count; ++i) {
        const dg_decor_rulepack *rp = c->rulepacks[i];
        dg_decor_rulepack_state st;
        u32 idx;
        if (!rp || rp->id == 0u) continue;
        st.id = rp->id;
        st.hash = dg_decor_rulepack_hash(rp);
        st.present = D_TRUE;
        st._pad32 = 0u;

        idx = rulepack_state_lower_bound(c, rp->id);
        if (idx < c->rulepack_state_count && c->rulepack_state[idx].id == rp->id) {
            c->rulepack_state[idx].present = D_TRUE;
            if (c->rulepack_state[idx].hash != st.hash) {
                c->rulepack_state[idx].hash = st.hash;
                dg_decor_dirty_mark_rulepack(&c->dirty, rp->id);
            }
        } else {
            if (reserve_rulepack_state(c, c->rulepack_state_count + 1u) != 0) return -3;
            if (idx < c->rulepack_state_count) {
                memmove(&c->rulepack_state[idx + 1u], &c->rulepack_state[idx],
                        sizeof(dg_decor_rulepack_state) * (size_t)(c->rulepack_state_count - idx));
            }
            c->rulepack_state[idx] = st;
            c->rulepack_state_count += 1u;
            dg_decor_dirty_mark_rulepack(&c->dirty, rp->id);
        }
    }

    /* Remove rulepack state entries that are no longer present (conservative: mark overrides dirty). */
    removed_rulepacks = 0u;
    for (i = 0u; i < c->rulepack_state_count; /* manual */) {
        if (!c->rulepack_state[i].present) {
            if (i + 1u < c->rulepack_state_count) {
                memmove(&c->rulepack_state[i], &c->rulepack_state[i + 1u],
                        sizeof(dg_decor_rulepack_state) * (size_t)(c->rulepack_state_count - i - 1u));
            }
            c->rulepack_state_count -= 1u;
            removed_rulepacks += 1u;
            continue;
        }
        i += 1u;
    }
    if (removed_rulepacks != 0u) {
        /* Removing a rulepack can affect unknown host sets; rebuild conservatively. */
        dg_decor_dirty_mark_overrides(&c->dirty);
    }

    /* Canonicalize override pointer list by id. */
    if (reserve_override_ptrs(c, in->override_count) != 0) return -4;
    c->override_count = in->override_count;
    for (i = 0u; i < in->override_count; ++i) {
        c->overrides[i] = &in->overrides[i];
    }
    if (c->override_count > 1u) {
        qsort(c->overrides, (size_t)c->override_count, sizeof(c->overrides[0]), cmp_override_ptr);
    }

    /* Override hash detection. */
    {
        u64 h = hash_overrides_sorted(c);
        if (c->overrides_hash != h) {
            c->overrides_hash = h;
            dg_decor_dirty_mark_overrides(&c->dirty);
        }
    }

    /* Canonicalize host catalog by host key (insertion order independent). */
    tmp_hosts = (dg_decor_host_desc *)malloc(sizeof(dg_decor_host_desc) * (size_t)in->host_count);
    if (!tmp_hosts && in->host_count != 0u) return -5;
    for (i = 0u; i < in->host_count; ++i) {
        tmp_hosts[i] = in->hosts[i];
        canon_range(&tmp_hosts[i].primary0, &tmp_hosts[i].primary1);
        canon_range(&tmp_hosts[i].secondary0, &tmp_hosts[i].secondary1);
    }
    if (in->host_count > 1u) {
        qsort(tmp_hosts, (size_t)in->host_count, sizeof(dg_decor_host_desc), cmp_host_desc);
    }

    for (i = 0u; i < c->host_count; ++i) {
        c->hosts[i].present = D_FALSE;
    }
    for (i = 0u; i < c->chunk_count; ++i) {
        c->chunks[i].present = D_FALSE;
    }

    for (i = 0u; i < in->host_count; ++i) {
        const dg_decor_host_desc *hd = &tmp_hosts[i];
        dg_decor_compiled_host *ch;
        d_bool added;
        u64 new_hash;
        dg_chunk_id old_chunk;

        ch = get_or_add_host(c, hd, &added);
        if (!ch) continue;

        old_chunk = ch->desc.chunk_id;
        ch->present = D_TRUE;

        new_hash = hash_host_desc(hd);
        if (added || ch->desc_hash != new_hash) {
            ch->desc = *hd;
            ch->desc_hash = new_hash;
            dg_decor_dirty_mark_host(&c->dirty, &ch->desc.host, ch->desc.chunk_id);
            if (!added && old_chunk != 0u && old_chunk != ch->desc.chunk_id) {
                dg_decor_dirty_mark_chunk(&c->dirty, old_chunk);
            }
        } else {
            ch->desc = *hd;
        }

        /* Ensure chunk record exists. */
        {
            dg_decor_compiled_chunk *cc = get_or_add_chunk(c, ch->desc.chunk_id);
            if (cc) cc->present = D_TRUE;
        }
    }

    free(tmp_hosts);

    /* Remove hosts that disappeared. */
    for (i = 0u; i < c->host_count; /* manual */) {
        if (!c->hosts[i].present) {
            dg_chunk_id old_chunk = c->hosts[i].desc.chunk_id;
            if (c->hosts[i].items) free(c->hosts[i].items);
            if (i + 1u < c->host_count) {
                memmove(&c->hosts[i], &c->hosts[i + 1u], sizeof(dg_decor_compiled_host) * (size_t)(c->host_count - i - 1u));
            }
            c->host_count -= 1u;
            if (old_chunk != 0u) dg_decor_dirty_mark_chunk(&c->dirty, old_chunk);
            continue;
        }
        i += 1u;
    }

    /* Remove chunks that disappeared. */
    for (i = 0u; i < c->chunk_count; /* manual */) {
        if (!c->chunks[i].present) {
            dg_decor_instances_free(&c->chunks[i].instances);
            dg_decor_tiles_free(&c->chunks[i].tiles);
            if (i + 1u < c->chunk_count) {
                memmove(&c->chunks[i], &c->chunks[i + 1u], sizeof(dg_decor_compiled_chunk) * (size_t)(c->chunk_count - i - 1u));
            }
            c->chunk_count -= 1u;
            continue;
        }
        i += 1u;
    }

    /* Expand dirty rulepacks into dirty hosts immediately (so host/chunk dirtiness is queryable post-sync). */
    for (i = 0u; i < c->dirty.rulepack_count; ++i) {
        u32 rpi;
        dg_decor_dirty_rulepack *drp = &c->dirty.rulepacks[i];
        if (!drp->dirty) continue;
        for (rpi = 0u; rpi < c->rulepack_count; ++rpi) {
            u32 hi;
            const dg_decor_rulepack *rp = c->rulepacks[rpi];
            if (!rp || rp->id != drp->rulepack_id) continue;
            for (hi = 0u; hi < c->host_count; ++hi) {
                const dg_decor_compiled_host *ch = &c->hosts[hi];
                if (dg_decor_rulepack_matches_host(rp, &ch->desc.host)) {
                    dg_decor_dirty_mark_host(&c->dirty, &ch->desc.host, ch->desc.chunk_id);
                }
            }
        }
    }

    /* Overrides change conservatively dirties all hosts. */
    if (c->dirty.overrides_dirty) {
        for (i = 0u; i < c->host_count; ++i) {
            dg_decor_dirty_mark_host(&c->dirty, &c->hosts[i].desc.host, c->hosts[i].desc.chunk_id);
        }
    }

    if (seed_changed) {
        for (i = 0u; i < c->host_count; ++i) {
            dg_decor_dirty_mark_host(&c->dirty, &c->hosts[i].desc.host, c->hosts[i].desc.chunk_id);
        }
    }

    return 0;
}

static void make_key_for_host(dg_order_key *out_key, const dg_decor_host_desc *hd) {
    dg_order_key k;
    dg_order_key_clear(&k);
    k.phase = (u16)DG_PH_TOPOLOGY;
    k._pad16 = 0u;
    k.domain_id = 0u;
    k.chunk_id = hd ? hd->chunk_id : 0u;
    k.entity_id = 0u;
    k.component_id = 0u;
    k.type_id = ((u64)DG_DECOR_WORK_HOST << 32) | (u64)(u32)(hd ? hd->host.kind : 0u);
    k.seq = 0u;
    k._pad32 = 0u;

    if (hd) {
        switch (hd->host.kind) {
        case DG_DECOR_HOST_TERRAIN_PATCH:
            k.entity_id = (dg_entity_id)hd->chunk_id;
            break;
        case DG_DECOR_HOST_TRANS_SLOT_SURFACE:
            k.entity_id = (dg_entity_id)hd->host.u.trans_slot_surface.alignment_id;
            k.component_id = (u64)hd->host.u.trans_slot_surface.slot_id;
            k.seq = hd->host.u.trans_slot_surface.segment_index;
            break;
        case DG_DECOR_HOST_STRUCT_SURFACE:
            k.entity_id = (dg_entity_id)hd->host.u.struct_surface.struct_id;
            k.component_id = (u64)hd->host.u.struct_surface.surface_id;
            break;
        case DG_DECOR_HOST_ROOM_SURFACE:
            k.entity_id = (dg_entity_id)hd->host.u.room_surface.room_id;
            k.component_id = (u64)hd->host.u.room_surface.surface_id;
            break;
        case DG_DECOR_HOST_SOCKET:
            k.entity_id = (dg_entity_id)hd->host.u.socket.socket_id;
            break;
        default:
            break;
        }
    }

    if (out_key) *out_key = k;
}

static void make_key_for_chunk_tiles(dg_order_key *out_key, dg_chunk_id chunk_id) {
    dg_order_key k;
    dg_order_key_clear(&k);
    k.phase = (u16)DG_PH_TOPOLOGY;
    k._pad16 = 0u;
    k.domain_id = 0u;
    k.chunk_id = chunk_id;
    k.entity_id = 0xFFFFFFFFFFFFFFFFULL; /* ensure tile work runs after host work within chunk */
    k.component_id = 0u;
    k.type_id = (dg_type_id)DG_DECOR_WORK_CHUNK_TILES;
    k.seq = 0u;
    k._pad32 = 0u;
    if (out_key) *out_key = k;
}

int dg_decor_compiler_enqueue_dirty(dg_decor_compiler *c, dg_tick tick) {
    u32 i;
    if (!c) return -1;

    /* Enqueue host work. */
    for (i = 0u; i < c->dirty.host_count; ++i) {
        dg_decor_dirty_host *dh = &c->dirty.hosts[i];
        const dg_decor_compiled_host *ch;
        dg_work_item it;
        if (!dh->dirty) continue;
        ch = dg_decor_compiler_find_host(c, &dh->host);
        if (!ch) continue;
        dg_work_item_clear(&it);
        make_key_for_host(&it.key, &ch->desc);
        it.work_type_id = DG_DECOR_WORK_HOST;
        it.cost_units = 1u;
        it.enqueue_tick = tick;
        (void)dg_work_queue_push(&c->work_q, &it);
        dh->dirty = D_FALSE;
    }

    /* Enqueue chunk tile work. */
    for (i = 0u; i < c->dirty.chunk_count; ++i) {
        dg_decor_dirty_chunk *dc = &c->dirty.chunks[i];
        dg_work_item it;
        if (!dc->dirty) continue;
        dg_work_item_clear(&it);
        make_key_for_chunk_tiles(&it.key, dc->chunk_id);
        it.work_type_id = DG_DECOR_WORK_CHUNK_TILES;
        it.cost_units = 1u;
        it.enqueue_tick = tick;
        (void)dg_work_queue_push(&c->work_q, &it);
        dc->dirty = D_FALSE;
    }

    /* Dirty sources cleared at enqueue time. */
    c->dirty.overrides_dirty = D_FALSE;
    for (i = 0u; i < c->dirty.rulepack_count; ++i) {
        c->dirty.rulepacks[i].dirty = D_FALSE;
    }

    return 0;
}

static dg_decor_host decode_host_from_key(const dg_order_key *k) {
    dg_decor_host h;
    dg_decor_host_clear(&h);
    if (!k) return h;

    h.kind = (dg_decor_host_kind)(u32)(k->type_id & 0xFFFFFFFFu);
    h._pad32 = 0u;

    switch (h.kind) {
    case DG_DECOR_HOST_TERRAIN_PATCH:
        h.u.terrain_patch.chunk_id = (dg_chunk_id)k->entity_id;
        break;
    case DG_DECOR_HOST_TRANS_SLOT_SURFACE:
        h.u.trans_slot_surface.alignment_id = (dg_trans_alignment_id)k->entity_id;
        h.u.trans_slot_surface.slot_id = (dg_trans_slot_id)k->component_id;
        h.u.trans_slot_surface.segment_index = k->seq;
        break;
    case DG_DECOR_HOST_STRUCT_SURFACE:
        h.u.struct_surface.struct_id = (dg_struct_id)k->entity_id;
        h.u.struct_surface.surface_id = (dg_struct_surface_id)k->component_id;
        break;
    case DG_DECOR_HOST_ROOM_SURFACE:
        h.u.room_surface.room_id = (dg_struct_room_id)k->entity_id;
        h.u.room_surface.surface_id = (dg_struct_surface_id)k->component_id;
        break;
    case DG_DECOR_HOST_SOCKET:
        h.u.socket.socket_id = (u64)k->entity_id;
        break;
    default:
        break;
    }

    return h;
}

static void process_host_work(dg_decor_compiler *c, const dg_order_key *k) {
    dg_decor_host h;
    dg_decor_compiled_host *ch;
    u32 idx;
    if (!c || !k) return;
    h = decode_host_from_key(k);
    idx = host_lower_bound(c, &h);
    if (idx >= c->host_count) return;
    if (dg_decor_host_cmp(&c->hosts[idx].desc.host, &h) != 0) return;
    ch = &c->hosts[idx];

    generate_baseline_for_host(c, ch);
    apply_overrides_for_host(c, ch);
}

static void process_chunk_tiles_work(dg_decor_compiler *c, dg_chunk_id chunk_id, const d_world_frame *frames, dg_tick tick, dg_round_mode round_mode) {
    dg_decor_compiled_chunk *cc;
    u32 idx;
    u32 hi;
    u32 total;
    dg_decor_item *scratch;
    u32 w;

    if (!c) return;
    if (chunk_id == 0u) return;
    idx = chunk_lower_bound(c, chunk_id);
    if (idx >= c->chunk_count) return;
    if (c->chunks[idx].chunk_id != chunk_id) return;
    cc = &c->chunks[idx];

    total = 0u;
    for (hi = 0u; hi < c->host_count; ++hi) {
        const dg_decor_compiled_host *h = &c->hosts[hi];
        if (h->desc.chunk_id != chunk_id) continue;
        total += h->item_count;
    }

    if (total == 0u) {
        dg_decor_instances_clear(&cc->instances);
        dg_decor_tiles_clear(&cc->tiles);
        return;
    }

    scratch = (dg_decor_item *)malloc(sizeof(dg_decor_item) * (size_t)total);
    if (!scratch) return;

    w = 0u;
    for (hi = 0u; hi < c->host_count; ++hi) {
        const dg_decor_compiled_host *h = &c->hosts[hi];
        u32 j;
        if (h->desc.chunk_id != chunk_id) continue;
        for (j = 0u; j < h->item_count; ++j) {
            scratch[w++] = h->items[j];
        }
    }

    if (w != total) total = w;

    if (total > 1u) {
        qsort(scratch, (size_t)total, sizeof(dg_decor_item), cmp_item_qsort);
    }

    (void)dg_decor_instances_build_from_items(&cc->instances, scratch, total, chunk_id, frames, tick, round_mode);
    (void)dg_decor_tiles_build_from_instances(&cc->tiles, &cc->instances);
    free(scratch);
}

u32 dg_decor_compiler_process(
    dg_decor_compiler      *c,
    const d_world_frame    *frames,
    dg_tick                 tick,
    dg_round_mode           round_mode,
    u32                     budget_units
) {
    u32 processed = 0u;
    dg_work_item it;

    if (!c) return 0u;

    while (budget_units > 0u) {
        const dg_work_item *next = dg_work_queue_peek_next(&c->work_q);
        if (!next) break;
        if (next->cost_units > budget_units) break;

        if (!dg_work_queue_pop_next(&c->work_q, &it)) break;
        if (it.cost_units > budget_units) break;
        budget_units -= it.cost_units;

        if (it.work_type_id == DG_DECOR_WORK_HOST) {
            process_host_work(c, &it.key);
        } else if (it.work_type_id == DG_DECOR_WORK_CHUNK_TILES) {
            process_chunk_tiles_work(c, it.key.chunk_id, frames, tick, round_mode);
        }

        processed += 1u;
    }

    return processed;
}

u32 dg_decor_compiler_pending_work(const dg_decor_compiler *c) {
    if (!c) return 0u;
    return dg_work_queue_count(&c->work_q);
}

const dg_decor_compiled_chunk *dg_decor_compiler_find_chunk(const dg_decor_compiler *c, dg_chunk_id chunk_id) {
    u32 idx;
    if (!c || chunk_id == 0u) return (const dg_decor_compiled_chunk *)0;
    idx = chunk_lower_bound(c, chunk_id);
    if (idx < c->chunk_count && c->chunks[idx].chunk_id == chunk_id) {
        return &c->chunks[idx];
    }
    return (const dg_decor_compiled_chunk *)0;
}

const dg_decor_compiled_host *dg_decor_compiler_find_host(const dg_decor_compiler *c, const dg_decor_host *host) {
    u32 idx;
    if (!c || !host) return (const dg_decor_compiled_host *)0;
    idx = host_lower_bound(c, host);
    if (idx < c->host_count && dg_decor_host_cmp(&c->hosts[idx].desc.host, host) == 0) {
        return &c->hosts[idx];
    }
    return (const dg_decor_compiled_host *)0;
}
