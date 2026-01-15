/*
FILE: source/domino/decor/compile/dg_decor_promote.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_promote
RESPONSIBILITY: Implements `dg_decor_promote`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR promotion plumbing (C89). */
#include "decor/compile/dg_decor_promote.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "sim/sched/dg_phase.h"

void dg_decor_promotion_list_init(dg_decor_promotion_list *l) {
    if (!l) return;
    memset(l, 0, sizeof(*l));
}

void dg_decor_promotion_list_free(dg_decor_promotion_list *l) {
    if (!l) return;
    if (l->items) free(l->items);
    dg_decor_promotion_list_init(l);
}

void dg_decor_promotion_list_clear(dg_decor_promotion_list *l) {
    if (!l) return;
    l->count = 0u;
}

int dg_decor_promotion_list_reserve(dg_decor_promotion_list *l, u32 capacity) {
    dg_decor_promotion_req *arr;
    u32 new_cap;
    if (!l) return -1;
    if (capacity <= l->capacity) return 0;
    new_cap = l->capacity ? l->capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_promotion_req *)realloc(l->items, sizeof(dg_decor_promotion_req) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > l->capacity) {
        memset(&arr[l->capacity], 0, sizeof(dg_decor_promotion_req) * (size_t)(new_cap - l->capacity));
    }
    l->items = arr;
    l->capacity = new_cap;
    return 0;
}

static int cmp_req_key(const void *pa, const void *pb) {
    const dg_decor_promotion_req *a = (const dg_decor_promotion_req *)pa;
    const dg_decor_promotion_req *b = (const dg_decor_promotion_req *)pb;
    return dg_order_key_cmp(&a->key, &b->key);
}

static dg_order_key make_key(dg_tick tick, dg_domain_id domain_id, dg_chunk_id chunk_id, dg_decor_id decor_id) {
    dg_order_key k;
    dg_order_key_clear(&k);
    (void)tick;
    k.phase = (u16)DG_PH_TOPOLOGY;
    k._pad16 = 0u;
    k.domain_id = domain_id;
    k.chunk_id = chunk_id;
    k.entity_id = (dg_entity_id)decor_id; /* stable link back to decor_id */
    k.component_id = 0u;
    k.type_id = (dg_type_id)DG_DECOR_DELTA_PROMOTE;
    k.seq = 0u;
    k._pad32 = 0u;
    return k;
}

int dg_decor_promote_collect(
    dg_decor_promotion_list *out,
    const dg_decor_instances *instances,
    dg_tick                   tick,
    dg_domain_id              domain_id
) {
    u32 i;
    u32 count;

    if (!out) return -1;
    dg_decor_promotion_list_clear(out);
    if (!instances || instances->count == 0u) return 0;

    /* Count promotables. */
    count = 0u;
    for (i = 0u; i < instances->count; ++i) {
        if ((instances->items[i].flags & DG_DECOR_ITEM_F_PROMOTABLE) != 0u) {
            count += 1u;
        }
    }

    if (count == 0u) return 0;
    if (dg_decor_promotion_list_reserve(out, count) != 0) return -2;

    out->count = 0u;
    for (i = 0u; i < instances->count; ++i) {
        const dg_decor_instance *inst = &instances->items[i];
        if ((inst->flags & DG_DECOR_ITEM_F_PROMOTABLE) == 0u) continue;
        out->items[out->count].chunk_id = inst->chunk_id;
        out->items[out->count].decor_id = inst->decor_id;
        out->items[out->count].decor_type_id = inst->decor_type_id;
        out->items[out->count].key = make_key(tick, domain_id, inst->chunk_id, inst->decor_id);
        out->count += 1u;
    }

    /* Canonicalize order. */
    qsort(out->items, (size_t)out->count, sizeof(dg_decor_promotion_req), cmp_req_key);
    return 0;
}

