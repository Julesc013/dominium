#include <stdlib.h>
#include <string.h>

#include "sim/lod/dg_interest.h"

#include "core/det_invariants.h"

/* Quantization for interest volumes (q16_16): 1/16m resolution. */
#define DG_IV_QUANT_RSHIFT 12u

static q16_16 dg_iv_quantize_q16_16(q16_16 v) {
    i32 raw = (i32)v;
    i32 q = D_DET_RSHIFT_NEAR_I32(raw, DG_IV_QUANT_RSHIFT);
    return (q16_16)(q << DG_IV_QUANT_RSHIFT);
}

static dg_lod_obj_pos dg_iv_quantize_pos(dg_lod_obj_pos p) {
    p.x = dg_iv_quantize_q16_16(p.x);
    p.y = dg_iv_quantize_q16_16(p.y);
    p.z = dg_iv_quantize_q16_16(p.z);
    return p;
}

static q16_16 dg_iv_default_weight(dg_interest_volume_type t) {
    switch (t) {
        case DG_IV_PLAYER: return (q16_16)(1 << Q16_16_FRAC_BITS);
        case DG_IV_OWNERSHIP: return (q16_16)((1 << Q16_16_FRAC_BITS) / 2);
        case DG_IV_HAZARD: return (q16_16)((1 << Q16_16_FRAC_BITS) * 2);
        case DG_IV_ACTIVITY: return (q16_16)(1 << Q16_16_FRAC_BITS);
        case DG_IV_CRITICAL_INFRA: return (q16_16)((1 << Q16_16_FRAC_BITS) * 3);
        default: break;
    }
    return (q16_16)(1 << Q16_16_FRAC_BITS);
}

static void dg_iv_quantize_volume(dg_interest_volume *v) {
    if (!v) return;
    v->center = dg_iv_quantize_pos(v->center);
    v->radius = dg_iv_quantize_q16_16(v->radius);
    v->half_extents = dg_iv_quantize_pos(v->half_extents);
    if (v->weight == 0) {
        v->weight = dg_iv_default_weight(v->type);
    }
}

void dg_interest_list_init(dg_interest_list *l) {
    if (!l) return;
    memset(l, 0, sizeof(*l));
}

void dg_interest_list_free(dg_interest_list *l) {
    if (!l) return;
    if (l->owns_storage && l->volumes) {
        free(l->volumes);
    }
    dg_interest_list_init(l);
}

int dg_interest_list_reserve(dg_interest_list *l, u32 capacity) {
    dg_interest_volume *v;
    if (!l) return -1;
    dg_interest_list_free(l);
    if (capacity == 0u) return 0;
    v = (dg_interest_volume *)malloc(sizeof(dg_interest_volume) * (size_t)capacity);
    if (!v) return -2;
    memset(v, 0, sizeof(dg_interest_volume) * (size_t)capacity);
    l->volumes = v;
    l->capacity = capacity;
    l->count = 0u;
    l->owns_storage = D_TRUE;
    l->probe_refused = 0u;
    return 0;
}

void dg_interest_list_clear(dg_interest_list *l) {
    if (!l) return;
    l->count = 0u;
}

u32 dg_interest_list_count(const dg_interest_list *l) {
    return l ? l->count : 0u;
}

u32 dg_interest_list_probe_refused(const dg_interest_list *l) {
    return l ? l->probe_refused : 0u;
}

int dg_interest_list_push(dg_interest_list *l, const dg_interest_volume *v) {
    dg_interest_volume tmp;
    if (!l || !v || !l->volumes) return -1;
    if (l->count >= l->capacity) {
        l->probe_refused += 1u;
        return -2;
    }
    tmp = *v;
    dg_iv_quantize_volume(&tmp);
    l->volumes[l->count++] = tmp;
    return 0;
}

void dg_interest_init(dg_interest_ctx *ic) {
    if (!ic) return;
    memset(ic, 0, sizeof(*ic));
}

void dg_interest_free(dg_interest_ctx *ic) {
    if (!ic) return;
    if (ic->sources) {
        free(ic->sources);
    }
    dg_interest_init(ic);
}

int dg_interest_reserve(dg_interest_ctx *ic, u32 capacity) {
    dg_interest_source *s;
    if (!ic) return -1;
    dg_interest_free(ic);
    if (capacity == 0u) return 0;
    s = (dg_interest_source *)malloc(sizeof(dg_interest_source) * (size_t)capacity);
    if (!s) return -2;
    memset(s, 0, sizeof(dg_interest_source) * (size_t)capacity);
    ic->sources = s;
    ic->capacity = capacity;
    ic->count = 0u;
    ic->next_insert_index = 0u;
    ic->probe_refused = 0u;
    return 0;
}

static u32 dg_interest_upper_bound(const dg_interest_ctx *ic, u64 priority_key) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!ic) return 0u;
    hi = ic->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (ic->sources[mid].priority_key <= priority_key) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

int dg_interest_register_source(dg_interest_ctx *ic, dg_interest_source_fn fn, u64 priority_key, void *user_ctx) {
    dg_interest_source s;
    u32 idx;
    if (!ic || !fn) return -1;
    if (!ic->sources || ic->capacity == 0u || ic->count >= ic->capacity) {
        ic->probe_refused += 1u;
        return -2;
    }
    memset(&s, 0, sizeof(s));
    s.fn = fn;
    s.user_ctx = user_ctx;
    s.priority_key = priority_key;
    s.insert_index = ic->next_insert_index++;

    idx = dg_interest_upper_bound(ic, priority_key);
    if (idx < ic->count) {
        memmove(&ic->sources[idx + 1u], &ic->sources[idx], sizeof(dg_interest_source) * (size_t)(ic->count - idx));
    }
    ic->sources[idx] = s;
    ic->count += 1u;
    return 0;
}

u32 dg_interest_probe_refused(const dg_interest_ctx *ic) {
    return ic ? ic->probe_refused : 0u;
}

static int dg_interest_cmp_u64(u64 a, u64 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_interest_cmp_i32(i32 a, i32 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_interest_volume_cmp(const dg_interest_volume *a, const dg_interest_volume *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = dg_interest_cmp_u64((u64)a->type, (u64)b->type);
    if (c) return c;
    c = dg_interest_cmp_u64((u64)a->shape, (u64)b->shape);
    if (c) return c;
    c = dg_interest_cmp_u64((u64)a->domain_id, (u64)b->domain_id);
    if (c) return c;
    c = dg_interest_cmp_u64((u64)a->src_entity, (u64)b->src_entity);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->center.x, (i32)b->center.x);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->center.y, (i32)b->center.y);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->center.z, (i32)b->center.z);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->radius, (i32)b->radius);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->half_extents.x, (i32)b->half_extents.x);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->half_extents.y, (i32)b->half_extents.y);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->half_extents.z, (i32)b->half_extents.z);
    if (c) return c;
    c = dg_interest_cmp_i32((i32)a->weight, (i32)b->weight);
    if (c) return c;
    return 0;
}

static void dg_interest_list_insertion_sort(dg_interest_list *l) {
    u32 i;
    if (!l || !l->volumes) return;
    for (i = 1u; i < l->count; ++i) {
        dg_interest_volume key = l->volumes[i];
        u32 j = i;
        while (j > 0u && dg_interest_volume_cmp(&l->volumes[j - 1u], &key) > 0) {
            l->volumes[j] = l->volumes[j - 1u];
            --j;
        }
        l->volumes[j] = key;
    }
}

int dg_interest_collect(dg_interest_ctx *ic, dg_tick tick, dg_interest_list *out_list) {
    u32 i;
    if (!ic || !out_list) return -1;

    dg_interest_list_clear(out_list);

    for (i = 0u; i < ic->count; ++i) {
        if (ic->sources[i].fn) {
            ic->sources[i].fn(tick, out_list, ic->sources[i].user_ctx);
        }
    }

    /* Canonicalize list to make downstream hashing/replay comparisons stable. */
    dg_interest_list_insertion_sort(out_list);
    return 0;
}

static i64 dg_add_saturate_i64(i64 a, i64 b) {
    /* i64 bounds (two's complement; enforced by det_invariants.h). */
    const i64 I64_MAX = (i64)(u64)0x7FFFFFFFFFFFFFFFULL;
    const i64 I64_MIN = (i64)(-I64_MAX - 1);

    if (b > 0) {
        if (a > (I64_MAX - b)) {
            return I64_MAX;
        }
    } else if (b < 0) {
        if (a < (I64_MIN - b)) {
            return I64_MIN;
        }
    }
    return (i64)(a + b);
}

static i64 dg_sq_q16_16(q16_16 v) {
    i64 x = (i64)(i32)v;
    return x * x; /* q32_32 */
}

static i64 dg_dist2_q32_32(const dg_lod_obj_pos *a, const dg_lod_obj_pos *b) {
    q16_16 dx, dy, dz;
    i64 s;
    if (!a || !b) return 0;
    dx = (q16_16)((i32)a->x - (i32)b->x);
    dy = (q16_16)((i32)a->y - (i32)b->y);
    dz = (q16_16)((i32)a->z - (i32)b->z);
    s = dg_sq_q16_16(dx);
    s = dg_add_saturate_i64(s, dg_sq_q16_16(dy));
    s = dg_add_saturate_i64(s, dg_sq_q16_16(dz));
    if (s < 0) s = (i64)0x7FFFFFFFFFFFFFFFULL;
    return s;
}

d_bool dg_interest_contains(const dg_lod_obj_pos *obj_pos, const dg_interest_volume *v) {
    if (!obj_pos || !v) return D_FALSE;
    switch (v->shape) {
        case DG_IV_SHAPE_SPHERE: {
            i64 d2 = dg_dist2_q32_32(obj_pos, &v->center);
            i64 r2 = dg_sq_q16_16(v->radius);
            return (d2 <= r2) ? D_TRUE : D_FALSE;
        }
        case DG_IV_SHAPE_AABB: {
            i32 dx = (i32)obj_pos->x - (i32)v->center.x;
            i32 dy = (i32)obj_pos->y - (i32)v->center.y;
            i32 dz = (i32)obj_pos->z - (i32)v->center.z;
            i32 hx = (i32)v->half_extents.x;
            i32 hy = (i32)v->half_extents.y;
            i32 hz = (i32)v->half_extents.z;
            if (dx < 0) dx = -dx;
            if (dy < 0) dy = -dy;
            if (dz < 0) dz = -dz;
            return (dx <= hx && dy <= hy && dz <= hz) ? D_TRUE : D_FALSE;
        }
        default:
            break;
    }
    return D_FALSE;
}

static q16_16 dg_interest_score_sphere(const dg_interest_volume *v, const dg_lod_obj_pos *obj_pos) {
    i64 d2;
    i64 r2;
    if (!v || !obj_pos) return 0;
    d2 = dg_dist2_q32_32(obj_pos, &v->center);
    r2 = dg_sq_q16_16(v->radius);
    if (r2 <= 0) {
        return (d2 == 0) ? v->weight : 0;
    }
    if (d2 > r2) {
        return 0;
    }
    /* Two-tier deterministic falloff without division:
     * - within r/2 => full weight  (d2 <= r2/4)
     * - within r   => half weight  (d2 <= r2)
     */
    if (d2 <= (r2 >> 2)) {
        return v->weight;
    }
    return (q16_16)(v->weight >> 1);
}

static q16_16 dg_interest_score_aabb(const dg_interest_volume *v, const dg_lod_obj_pos *obj_pos) {
    if (!v || !obj_pos) return 0;
    return dg_interest_contains(obj_pos, v) ? v->weight : 0;
}

q16_16 dg_interest_score_object(
    const dg_lod_obj_key *obj_key,
    const dg_lod_obj_pos *obj_pos,
    dg_lod_class_id       class_id,
    const dg_interest_list *volumes
) {
    i64 sum = 0;
    u32 i;
    (void)obj_key;
    (void)class_id;

    if (!obj_pos || !volumes || !volumes->volumes) {
        return 0;
    }

    for (i = 0u; i < volumes->count; ++i) {
        const dg_interest_volume *v = &volumes->volumes[i];
        q16_16 contrib = 0;
        switch (v->shape) {
            case DG_IV_SHAPE_SPHERE: contrib = dg_interest_score_sphere(v, obj_pos); break;
            case DG_IV_SHAPE_AABB: contrib = dg_interest_score_aabb(v, obj_pos); break;
            default: contrib = 0; break;
        }
        sum += (i64)(i32)contrib;
        if (sum > (i64)0x7FFFFFFF) {
            sum = (i64)0x7FFFFFFF;
        } else if (sum < (i64)(-0x7FFFFFFF - 1)) {
            sum = (i64)(-0x7FFFFFFF - 1);
        }
    }

    return (q16_16)(i32)sum;
}
