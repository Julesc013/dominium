/*
FILE: source/domino/decor/model/dg_decor_rulepack.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_rulepack
RESPONSIBILITY: Implements `dg_decor_rulepack`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR rulepacks (C89). */
#include "decor/model/dg_decor_rulepack.h"

#include <stdlib.h>
#include <string.h>

#include "core/dg_det_hash.h"
#include "res/dg_tlv_canon.h"

static u64 dg_hash_bytes(u64 h, const unsigned char *p, u32 n) {
    u32 i;
    if (!p) return dg_det_hash_u64(h ^ 0xBADC0FFEE0DDF00DULL);
    for (i = 0u; i < n; ++i) {
        h = dg_det_hash_u64(h ^ (u64)p[i]);
    }
    return h;
}

static int dg_spawn_lower_bound(const dg_decor_rulepack *rp, dg_decor_type_id type_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!rp) return 0;
    hi = rp->spawn_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (rp->spawns[mid].decor_type_id >= type_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return (int)lo;
}

void dg_decor_rulepack_init(dg_decor_rulepack *rp) {
    if (!rp) return;
    memset(rp, 0, sizeof(*rp));
    rp->interval_q = 0;
    rp->start_q = 0;
}

void dg_decor_rulepack_free(dg_decor_rulepack *rp) {
    if (!rp) return;
    if (rp->spawns) free(rp->spawns);
    dg_decor_rulepack_init(rp);
}

int dg_decor_rulepack_reserve_spawns(dg_decor_rulepack *rp, u32 capacity) {
    dg_decor_spawn_template *arr;
    u32 new_cap;
    if (!rp) return -1;
    if (capacity <= rp->spawn_capacity) return 0;
    new_cap = rp->spawn_capacity ? rp->spawn_capacity : 4u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_spawn_template *)realloc(rp->spawns, sizeof(dg_decor_spawn_template) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > rp->spawn_capacity) {
        memset(&arr[rp->spawn_capacity], 0, sizeof(dg_decor_spawn_template) * (size_t)(new_cap - rp->spawn_capacity));
    }
    rp->spawns = arr;
    rp->spawn_capacity = new_cap;
    return 0;
}

int dg_decor_rulepack_set_spawn(dg_decor_rulepack *rp, const dg_decor_spawn_template *st) {
    u32 idx;
    if (!rp || !st) return -1;
    if (st->decor_type_id == 0u) return -2;

    idx = (u32)dg_spawn_lower_bound(rp, st->decor_type_id);
    if (idx < rp->spawn_count && rp->spawns[idx].decor_type_id == st->decor_type_id) {
        rp->spawns[idx] = *st;
        return 0;
    }

    if (dg_decor_rulepack_reserve_spawns(rp, rp->spawn_count + 1u) != 0) return -3;

    if (idx < rp->spawn_count) {
        memmove(&rp->spawns[idx + 1u], &rp->spawns[idx],
                sizeof(dg_decor_spawn_template) * (size_t)(rp->spawn_count - idx));
    }
    rp->spawns[idx] = *st;
    rp->spawn_count += 1u;
    return 0;
}

d_bool dg_decor_rulepack_matches_host(const dg_decor_rulepack *rp, const dg_decor_host *host) {
    if (!rp || !host) return D_FALSE;
    if (rp->selector.host_kind != host->kind) return D_FALSE;
    if (rp->selector.match_all_of_kind) return D_TRUE;
    return (dg_decor_host_cmp(&rp->selector.exact, host) == 0) ? D_TRUE : D_FALSE;
}

u64 dg_decor_rulepack_hash(const dg_decor_rulepack *rp) {
    u64 h = 0xDEC0D0C0DEC0D0C1ULL;
    u32 i;
    unsigned char tmp[256];
    u32 tmp_len;

    if (!rp) return 0u;

    h = dg_det_hash_u64(h ^ (u64)rp->id);
    h = dg_det_hash_u64(h ^ (u64)rp->selector.host_kind);
    h = dg_det_hash_u64(h ^ (u64)rp->selector.match_all_of_kind);
    h = dg_det_hash_u64(h ^ dg_decor_host_stable_id_u64(&rp->selector.exact));
    h = dg_det_hash_u64(h ^ (u64)(i64)rp->interval_q);
    h = dg_det_hash_u64(h ^ (u64)(i64)rp->start_q);

    for (i = 0u; i < rp->spawn_count; ++i) {
        const dg_decor_spawn_template *st = &rp->spawns[i];
        h = dg_det_hash_u64(h ^ (u64)st->decor_type_id);
        h = dg_det_hash_u64(h ^ (u64)st->flags);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.pos.x);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.pos.y);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.pos.z);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.rot.x);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.rot.y);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.rot.z);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.rot.w);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.incline);
        h = dg_det_hash_u64(h ^ (u64)(i64)st->local_offset.roll);

        /* Hash canonicalized params to avoid insertion-order dependence inside TLV. */
        tmp_len = 0u;
        if (st->params.ptr && st->params.len <= (u32)sizeof(tmp)) {
            if (dg_tlv_canon(st->params.ptr, st->params.len, tmp, (u32)sizeof(tmp), &tmp_len) == 0) {
                h = dg_hash_bytes(h, tmp, tmp_len);
            } else {
                h = dg_hash_bytes(h, st->params.ptr, st->params.len);
            }
        } else {
            h = dg_det_hash_u64(h ^ (u64)st->params.len);
            h = dg_hash_bytes(h, st->params.ptr, st->params.len);
        }
    }

    return h;
}
