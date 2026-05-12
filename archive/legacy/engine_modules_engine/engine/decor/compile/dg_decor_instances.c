/*
FILE: source/domino/decor/compile/dg_decor_instances.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_instances
RESPONSIBILITY: Implements `dg_decor_instances`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR compiled instance lists (C89). */
#include "decor/compile/dg_decor_instances.h"

#include <stdlib.h>
#include <string.h>

void dg_decor_instances_init(dg_decor_instances *out) {
    if (!out) return;
    memset(out, 0, sizeof(*out));
}

void dg_decor_instances_free(dg_decor_instances *out) {
    if (!out) return;
    if (out->items) free(out->items);
    dg_decor_instances_init(out);
}

void dg_decor_instances_clear(dg_decor_instances *out) {
    if (!out) return;
    out->count = 0u;
}

int dg_decor_instances_reserve(dg_decor_instances *out, u32 capacity) {
    dg_decor_instance *arr;
    u32 new_cap;
    if (!out) return -1;
    if (capacity <= out->capacity) return 0;
    new_cap = out->capacity ? out->capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_instance *)realloc(out->items, sizeof(dg_decor_instance) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > out->capacity) {
        memset(&arr[out->capacity], 0, sizeof(dg_decor_instance) * (size_t)(new_cap - out->capacity));
    }
    out->items = arr;
    out->capacity = new_cap;
    return 0;
}

int dg_decor_instances_build_from_items(
    dg_decor_instances  *out,
    const dg_decor_item *items,
    u32                  item_count,
    dg_chunk_id          chunk_id,
    const d_world_frame *frames,
    dg_tick              tick,
    dg_round_mode        round_mode
) {
    u32 i;
    int rc;

    if (!out) return -1;
    dg_decor_instances_clear(out);

    if (item_count == 0u) return 0;
    if (!items) return -2;
    if (dg_decor_instances_reserve(out, item_count) != 0) return -3;

    rc = 0;
    for (i = 0u; i < item_count; ++i) {
        const dg_decor_item *it = &items[i];
        dg_decor_instance *inst = &out->items[i];
        dg_pose pose;

        memset(inst, 0, sizeof(*inst));
        inst->chunk_id = chunk_id;
        inst->decor_id = it->decor_id;
        inst->decor_type_id = it->decor_type_id;
        inst->flags = it->flags;
        inst->_pad32 = 0u;
        inst->host = it->host;
        inst->params = it->params;

        if (dg_decor_item_eval_pose(it, frames, tick, round_mode, &pose) != 0) {
            /* Keep deterministic output even if evaluation fails. */
            pose = dg_pose_identity();
            rc = -4;
        }
        inst->world_pose = pose;
    }

    out->count = item_count;
    return rc;
}

