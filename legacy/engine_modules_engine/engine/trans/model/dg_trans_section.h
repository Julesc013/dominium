/*
FILE: source/domino/trans/model/dg_trans_section.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/model/dg_trans_section
RESPONSIBILITY: Defines internal contract for `dg_trans_section`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS cross-section archetypes (slot packing) (C89). */
#ifndef DG_TRANS_SECTION_H
#define DG_TRANS_SECTION_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "trans/model/dg_trans_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_trans_slot {
    dg_trans_slot_id slot_id; /* stable within the section archetype */

    /* Slot local offset in section frame: (t=right, h=up). */
    dg_q offset_t;
    dg_q offset_h;

    /* Axis-aligned envelope in section frame (non-negative). */
    dg_q width;
    dg_q height;

    /* Allowed occupant categories/type ids (canonical sorted). */
    dg_trans_occupant_type_id *allowed_types;
    u32                        allowed_type_count;
    u32                        allowed_type_capacity;

    /* Optional rail id for placements in this slot (0 means none). */
    dg_trans_rail_id rail_id;
} dg_trans_slot;

typedef struct dg_trans_section_archetype {
    dg_trans_section_archetype_id id;

    dg_trans_slot *slots; /* canonical sorted by slot_id */
    u32            slot_count;
    u32            slot_capacity;
} dg_trans_section_archetype;

void dg_trans_section_init(dg_trans_section_archetype *sec);
void dg_trans_section_free(dg_trans_section_archetype *sec);

int dg_trans_section_reserve_slots(dg_trans_section_archetype *sec, u32 capacity);

/* Add or update a slot by slot_id (canonical slot order maintained). */
int dg_trans_section_set_slot(dg_trans_section_archetype *sec, const dg_trans_slot *slot);

/* Replace the allowed type list for a slot (sorted, deduped). */
int dg_trans_section_slot_set_allowed_types(dg_trans_slot *slot, const dg_trans_occupant_type_id *types, u32 type_count);

/* Lookup helpers. */
dg_trans_slot *dg_trans_section_find_slot(dg_trans_section_archetype *sec, dg_trans_slot_id slot_id);
const dg_trans_slot *dg_trans_section_find_slot_const(const dg_trans_section_archetype *sec, dg_trans_slot_id slot_id);

/* Returns nonzero if slot allows the given occupant_type_id. */
int dg_trans_slot_allows_type(const dg_trans_slot *slot, dg_trans_occupant_type_id occupant_type_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_SECTION_H */

