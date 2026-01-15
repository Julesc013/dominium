/*
FILE: source/domino/struct/d_struct.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/d_struct
RESPONSIBILITY: Defines internal contract for `d_struct`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Structure/machine subsystem types (C89). */
#ifndef D_STRUCT_H
#define D_STRUCT_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"
#include "struct/d_struct_instance.h"
#include "struct/d_struct_proto.h"
#include "sim/d_sim.h"

#ifdef __cplusplus
extern "C" {
#endif

d_struct_instance_id d_struct_create(
    d_world       *w,
    d_structure_proto_id proto_id,
    q16_16        x, q16_16 y, q16_16 z,
    q16_16        yaw
);

d_struct_instance_id d_struct_spawn(
    d_world                 *w,
    const d_struct_instance *inst_template
);

int d_struct_destroy(
    d_world             *w,
    d_struct_instance_id id
);

const d_struct_instance *d_struct_get(d_world *w, d_struct_instance_id id);
d_struct_instance *d_struct_get_mutable(d_world *w, d_struct_instance_id id);
const d_struct_instance *d_struct_get_by_index(d_world *w, u32 index);
u32 d_struct_count(d_world *w);

int d_struct_get_inventory_summary(
    d_world     *w,
    d_entity_id  struct_eid,
    d_item_id   *out_item_id,
    u32         *out_count
);

/* Subsystem registration hook */
void d_struct_init(void);
int d_struct_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_STRUCT_H */
