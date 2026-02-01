/*
FILE: source/domino/core/d_container_state.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_container_state
RESPONSIBILITY: Implements `d_container_state`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "core/d_container_state.h"

static q16_16 dcontainer_q16_mul_u32(q16_16 a, u32 b) {
    i64 prod = (i64)a * (i64)(i32)b;
    if (prod > (i64)2147483647L) {
        return (q16_16)2147483647L;
    }
    if (prod < (i64)(-2147483647L - 1L)) {
        return (q16_16)(-2147483647L - 1L);
    }
    return (q16_16)(i32)prod;
}

static u32 dcontainer_fit_count(q16_16 remaining, q16_16 per_unit) {
    if (per_unit <= 0) {
        return 0xFFFFFFFFu;
    }
    if (remaining <= 0) {
        return 0u;
    }
    return (u32)((i64)remaining / (i64)per_unit);
}

int d_container_state_init(d_container_state *st, d_container_proto_id proto_id) {
    const d_proto_container *p;
    u32 alloc_slots;

    if (!st || proto_id == 0u) {
        return -1;
    }
    p = d_content_get_container(proto_id);
    if (!p) {
        return -1;
    }

    memset(st, 0, sizeof(*st));
    st->proto_id = proto_id;
    st->used_volume = 0;
    st->used_mass = 0;
    st->slot_count = p->slot_count;
    st->slots = (d_container_slot *)0;

    alloc_slots = (p->slot_count > 0u) ? (u32)p->slot_count : 1u;
    st->slots = (d_container_slot *)malloc(sizeof(d_container_slot) * alloc_slots);
    if (!st->slots) {
        memset(st, 0, sizeof(*st));
        return -1;
    }
    memset(st->slots, 0, sizeof(d_container_slot) * alloc_slots);
    return 0;
}

void d_container_state_free(d_container_state *st) {
    if (!st) {
        return;
    }
    if (st->slots) {
        free(st->slots);
    }
    memset(st, 0, sizeof(*st));
}

int d_container_pack_items(
    d_container_state *st,
    d_item_id          item_id,
    u32                count,
    u32               *packed_count
) {
    const d_proto_container *cp;
    const d_proto_item *ip;
    u32 can_pack;
    u32 by_mass;
    u32 by_vol;
    q16_16 remaining_mass;
    q16_16 remaining_vol;
    u32 i;

    if (packed_count) {
        *packed_count = 0u;
    }
    if (!st || item_id == 0u || !packed_count) {
        return -1;
    }
    if (count == 0u) {
        return 0;
    }
    cp = d_content_get_container(st->proto_id);
    ip = d_content_get_item(item_id);
    if (!cp || !ip) {
        return -1;
    }
    if (!st->slots) {
        return -1;
    }

    remaining_mass = (q16_16)((i64)cp->max_mass - (i64)st->used_mass);
    remaining_vol  = (q16_16)((i64)cp->max_volume - (i64)st->used_volume);

    by_mass = dcontainer_fit_count(remaining_mass, ip->unit_mass);
    by_vol  = dcontainer_fit_count(remaining_vol, ip->unit_volume);
    can_pack = count;
    if (by_mass < can_pack) can_pack = by_mass;
    if (by_vol < can_pack) can_pack = by_vol;

    if (can_pack == 0u) {
        *packed_count = 0u;
        return 0;
    }

    if (st->slot_count == 0u) {
        /* Bulk-only: default to single item type. */
        if (st->slots[0].item_id != 0u && st->slots[0].item_id != item_id) {
            *packed_count = 0u;
            return 0;
        }
        st->slots[0].item_id = item_id;
        st->slots[0].count += can_pack;
    } else {
        /* Slot-based: use existing slot if present, else first free. */
        d_container_slot *slot = (d_container_slot *)0;
        for (i = 0u; i < (u32)st->slot_count; ++i) {
            if (st->slots[i].item_id == item_id) {
                slot = &st->slots[i];
                break;
            }
        }
        if (!slot) {
            for (i = 0u; i < (u32)st->slot_count; ++i) {
                if (st->slots[i].item_id == 0u) {
                    slot = &st->slots[i];
                    slot->item_id = item_id;
                    slot->count = 0u;
                    break;
                }
            }
        }
        if (!slot) {
            *packed_count = 0u;
            return 0;
        }
        slot->count += can_pack;
    }

    st->used_mass   = (q16_16)((i64)st->used_mass + (i64)dcontainer_q16_mul_u32(ip->unit_mass, can_pack));
    st->used_volume = (q16_16)((i64)st->used_volume + (i64)dcontainer_q16_mul_u32(ip->unit_volume, can_pack));

    *packed_count = can_pack;
    return 0;
}

int d_container_unpack_items(
    d_container_state *st,
    d_item_id          item_id,
    u32                requested_count,
    u32               *unpacked_count
) {
    const d_proto_item *ip;
    u32 avail;
    u32 to_unpack;
    u32 i;

    if (unpacked_count) {
        *unpacked_count = 0u;
    }
    if (!st || item_id == 0u || !unpacked_count) {
        return -1;
    }
    if (requested_count == 0u) {
        return 0;
    }
    ip = d_content_get_item(item_id);
    if (!ip || !st->slots) {
        return -1;
    }

    if (st->slot_count == 0u) {
        if (st->slots[0].item_id != item_id) {
            *unpacked_count = 0u;
            return 0;
        }
        avail = st->slots[0].count;
        to_unpack = (requested_count < avail) ? requested_count : avail;
        st->slots[0].count -= to_unpack;
        if (st->slots[0].count == 0u) {
            st->slots[0].item_id = 0u;
        }
    } else {
        d_container_slot *slot = (d_container_slot *)0;
        for (i = 0u; i < (u32)st->slot_count; ++i) {
            if (st->slots[i].item_id == item_id) {
                slot = &st->slots[i];
                break;
            }
        }
        if (!slot) {
            *unpacked_count = 0u;
            return 0;
        }
        avail = slot->count;
        to_unpack = (requested_count < avail) ? requested_count : avail;
        slot->count -= to_unpack;
        if (slot->count == 0u) {
            slot->item_id = 0u;
        }
    }

    if (to_unpack > 0u) {
        q16_16 dm = dcontainer_q16_mul_u32(ip->unit_mass, to_unpack);
        q16_16 dv = dcontainer_q16_mul_u32(ip->unit_volume, to_unpack);
        st->used_mass = (q16_16)((i64)st->used_mass - (i64)dm);
        st->used_volume = (q16_16)((i64)st->used_volume - (i64)dv);
        if (st->used_mass < 0) st->used_mass = 0;
        if (st->used_volume < 0) st->used_volume = 0;
    }

    *unpacked_count = to_unpack;
    return 0;
}

