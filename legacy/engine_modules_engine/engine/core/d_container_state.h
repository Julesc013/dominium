/*
FILE: source/domino/core/d_container_state.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_container_state
RESPONSIBILITY: Defines internal contract for `d_container_state`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Container packing state (C89). */
#ifndef D_CONTAINER_STATE_H
#define D_CONTAINER_STATE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "content/d_content.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_container_slot_s {
    d_item_id item_id;
    u32       count;
} d_container_slot;

typedef struct d_container_state_s {
    d_container_proto_id proto_id;
    q16_16               used_volume;
    q16_16               used_mass;

    /* If proto slot_count==0 this is bulk-only. */
    u16                  slot_count;
    d_container_slot    *slots; /* optional dyn array; bulk-only uses slots[0] */
} d_container_state;

int  d_container_state_init(d_container_state *st, d_container_proto_id proto_id);
void d_container_state_free(d_container_state *st);

/* Generic packing/unpacking operations. */
int d_container_pack_items(
    d_container_state *st,
    d_item_id          item_id,
    u32                count,
    u32               *packed_count /* out */
);

int d_container_unpack_items(
    d_container_state *st,
    d_item_id          item_id,
    u32                requested_count,
    u32               *unpacked_count /* out */
);

#ifdef __cplusplus
}
#endif

#endif /* D_CONTAINER_STATE_H */

