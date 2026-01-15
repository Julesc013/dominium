/*
FILE: source/domino/sim/dg_rebuild_work.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/dg_rebuild_work
RESPONSIBILITY: Implements `dg_rebuild_work`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "sim/dg_rebuild_work.h"

#define DG_REBUILD_ITEM_ID_MASK 0x00FFFFFFFFFFFFFFULL

u64 dg_rebuild_pack_component(dg_rebuild_work_kind kind, u64 item_id) {
    u64 k = ((u64)(u32)kind) & 0xFFULL;
    u64 id = item_id & DG_REBUILD_ITEM_ID_MASK;
    return (k << 56) | id;
}

dg_rebuild_work_kind dg_rebuild_unpack_kind(u64 component_id) {
    return (dg_rebuild_work_kind)((u32)((component_id >> 56) & 0xFFULL));
}

u64 dg_rebuild_unpack_item_id(u64 component_id) {
    return component_id & DG_REBUILD_ITEM_ID_MASK;
}

int dg_rebuild_work_from_item(const dg_work_item *it, dg_rebuild_work *out) {
    dg_rebuild_work w;
    u64 comp;
    if (!it || !out) {
        return -1;
    }
    memset(&w, 0, sizeof(w));
    w.graph_type_id = (dg_graph_type_id)it->key.type_id;
    w.graph_instance_id = (dg_graph_instance_id)it->key.entity_id;
    w.part_id = (dg_part_id)it->key.chunk_id;

    comp = it->key.component_id;
    w.kind = dg_rebuild_unpack_kind(comp);
    w.item_id = dg_rebuild_unpack_item_id(comp);

    *out = w;
    return 0;
}

