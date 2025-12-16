/*
FILE: source/domino/trans/model/dg_trans_ids.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/model/dg_trans_ids
RESPONSIBILITY: Implements `dg_trans_ids`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS stable identifiers and canonical ordering helpers (C89).
 *
 * TRANS models are referenced by stable numeric IDs and MUST define total
 * ordering for all deterministic iteration and compilation.
 */
#ifndef DG_TRANS_IDS_H
#define DG_TRANS_IDS_H

#include "domino/core/types.h"

#include "core/det_invariants.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dg_trans_alignment_id;
typedef u64 dg_trans_junction_id;
typedef u64 dg_trans_section_archetype_id;
typedef u64 dg_trans_slot_id;
typedef u64 dg_trans_rail_id;
typedef u64 dg_trans_occupant_type_id;
typedef u64 dg_trans_occupant_instance_id;

typedef struct dg_trans_segment_id {
    dg_trans_alignment_id alignment_id;
    u32                   segment_index; /* 0-based within alignment */
} dg_trans_segment_id;

static int dg_trans_segment_id_cmp(const dg_trans_segment_id *a, const dg_trans_segment_id *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = D_DET_CMP_U64(a->alignment_id, b->alignment_id);
    if (c) return c;
    c = D_DET_CMP_U32(a->segment_index, b->segment_index);
    if (c) return c;
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_IDS_H */

