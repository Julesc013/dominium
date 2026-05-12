/*
FILE: source/domino/trans/compile/dg_trans_slotmap.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/compile/dg_trans_slotmap
RESPONSIBILITY: Implements `dg_trans_slotmap`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS slot occupancy compilation (C89). */
#include "trans/compile/dg_trans_slotmap.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "domino/core/fixed.h"

dg_trans_rail_coord dg_trans_rail_coord_make(dg_trans_alignment_id alignment_id, dg_q s, dg_trans_slot_id slot_id, dg_q local_u) {
    dg_trans_rail_coord r;
    r.alignment_id = alignment_id;
    r.s = s;
    r.slot_id = slot_id;
    r.local_u = local_u;
    return r;
}

void dg_trans_segment_slotmap_init(dg_trans_segment_slotmap *m) {
    if (!m) return;
    memset(m, 0, sizeof(*m));
}

void dg_trans_segment_slotmap_free(dg_trans_segment_slotmap *m) {
    if (!m) return;
    if (m->items) free(m->items);
    dg_trans_segment_slotmap_init(m);
}

void dg_trans_segment_slotmap_clear(dg_trans_segment_slotmap *m) {
    if (!m) return;
    m->count = 0u;
}

int dg_trans_segment_slotmap_reserve(dg_trans_segment_slotmap *m, u32 capacity) {
    dg_trans_slot_occupancy *items;
    u32 new_cap;
    if (!m) return -1;
    if (capacity <= m->capacity) return 0;
    new_cap = m->capacity ? m->capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    items = (dg_trans_slot_occupancy *)realloc(m->items, sizeof(dg_trans_slot_occupancy) * (size_t)new_cap);
    if (!items) return -2;
    if (new_cap > m->capacity) {
        memset(&items[m->capacity], 0, sizeof(dg_trans_slot_occupancy) * (size_t)(new_cap - m->capacity));
    }
    m->items = items;
    m->capacity = new_cap;
    return 0;
}

static int dg_trans_occ_cmp(const dg_trans_slot_occupancy *a, const dg_trans_slot_occupancy *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = D_DET_CMP_U64(a->slot_id, b->slot_id); if (c) return c;
    c = D_DET_CMP_U64(a->occupant_instance_id, b->occupant_instance_id); if (c) return c;
    c = D_DET_CMP_U64(a->occupant_type_id, b->occupant_type_id); if (c) return c;
    return 0;
}

static void dg_trans_occ_insertion_sort(dg_trans_slot_occupancy *v, u32 count) {
    u32 i;
    if (!v || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        dg_trans_slot_occupancy key = v[i];
        u32 j = i;
        while (j > 0u && dg_trans_occ_cmp(&key, &v[j - 1u]) < 0) {
            v[j] = v[j - 1u];
            j -= 1u;
        }
        v[j] = key;
    }
}

static int dg_trans_attachment_cmp_local(const void *pa, const void *pb) {
    const dg_trans_attachment *a = (const dg_trans_attachment *)pa;
    const dg_trans_attachment *b = (const dg_trans_attachment *)pb;
    return dg_trans_attachment_cmp(a, b);
}

static void dg_trans_attachment_insertion_sort(dg_trans_attachment *v, u32 count) {
    u32 i;
    (void)dg_trans_attachment_cmp_local;
    if (!v || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        dg_trans_attachment key = v[i];
        u32 j = i;
        while (j > 0u && dg_trans_attachment_cmp(&key, &v[j - 1u]) < 0) {
            v[j] = v[j - 1u];
            j -= 1u;
        }
        v[j] = key;
    }
}

static int dg_trans_slot_is_free_for_interval(
    const dg_trans_attachment *assigned,
    const dg_trans_slot_id    *assigned_slot_ids,
    u32                        assigned_count,
    dg_trans_slot_id           slot_id,
    dg_q                        s0,
    dg_q                        s1
) {
    u32 i;
    if (!assigned || !assigned_slot_ids) return 1;
    for (i = 0u; i < assigned_count; ++i) {
        if (assigned_slot_ids[i] != slot_id) continue;
        if (dg_trans_attachment_overlaps(&assigned[i], s0, s1)) {
            return 0;
        }
    }
    return 1;
}

int dg_trans_slotmap_rebuild_range(
    dg_trans_segment_slotmap         *slotmaps,
    u32                               slotmap_count,
    const dg_trans_microseg          *segs,
    u32                               seg_count,
    dg_trans_alignment_id             alignment_id,
    const dg_trans_section_archetype *section,
    const dg_trans_attachment        *attachments,
    u32                               attachment_count,
    u32                               seg0,
    u32                               seg1
) {
    u32 i;
    u32 filtered_count = 0u;
    dg_trans_attachment *filtered = (dg_trans_attachment *)0;
    dg_trans_slot_id *resolved = (dg_trans_slot_id *)0;
    int rc = 0;

    if (!slotmaps || !segs || !section) return -1;
    if (seg_count != slotmap_count) return -2;
    if (alignment_id == 0u) return -3;

    if (seg_count == 0u) return 0;
    if (seg0 >= seg_count) return 0;
    if (seg1 >= seg_count) seg1 = seg_count - 1u;
    if (seg1 < seg0) return 0;

    /* Count and copy attachments for this alignment. */
    for (i = 0u; i < attachment_count; ++i) {
        if (attachments[i].alignment_id == alignment_id) {
            filtered_count += 1u;
        }
    }

    filtered = (dg_trans_attachment *)0;
    resolved = (dg_trans_slot_id *)0;
    if (filtered_count != 0u) {
        filtered = (dg_trans_attachment *)malloc(sizeof(dg_trans_attachment) * (size_t)filtered_count);
        if (!filtered) return -4;
        resolved = (dg_trans_slot_id *)malloc(sizeof(dg_trans_slot_id) * (size_t)filtered_count);
        if (!resolved) {
            free(filtered);
            return -5;
        }
        memset(resolved, 0, sizeof(dg_trans_slot_id) * (size_t)filtered_count);

        filtered_count = 0u;
        for (i = 0u; i < attachment_count; ++i) {
            if (attachments[i].alignment_id == alignment_id) {
                filtered[filtered_count++] = attachments[i];
            }
        }
        dg_trans_attachment_insertion_sort(filtered, filtered_count);

        /* Resolve slot assignments deterministically (explicit first due to ordering). */
        for (i = 0u; i < filtered_count; ++i) {
            const dg_trans_attachment *a = &filtered[i];
            dg_trans_slot_id slot_id = 0u;

            if (a->slot.kind == DG_TRANS_SLOT_ASSIGN_EXPLICIT) {
                slot_id = a->slot.slot_id;
            } else {
                /* Auto-pack: greedy in canonical slot order, avoiding overlap in the same slot when possible. */
                u32 sidx;
                dg_trans_slot_id fallback = 0u;
                for (sidx = 0u; sidx < section->slot_count; ++sidx) {
                    const dg_trans_slot *slt = &section->slots[sidx];
                    if (!dg_trans_slot_allows_type(slt, a->occupant_type_id)) continue;
                    if (fallback == 0u) fallback = slt->slot_id;
                    if (dg_trans_slot_is_free_for_interval(filtered, resolved, i, slt->slot_id, a->s0, a->s1)) {
                        slot_id = slt->slot_id;
                        break;
                    }
                }
                if (slot_id == 0u) {
                    slot_id = fallback; /* deterministic co-location fallback */
                }
            }

            resolved[i] = slot_id;
        }
    }

    /* Rebuild requested segment slotmaps. */
    for (i = seg0; i <= seg1; ++i) {
        dg_trans_segment_slotmap *m = &slotmaps[i];
        dg_q s_begin = segs[i].s_begin;
        dg_q s_end = segs[i].s_end;
        u32 aidx;

        dg_trans_segment_slotmap_clear(m);

        if (!filtered || filtered_count == 0u) {
            continue;
        }

        for (aidx = 0u; aidx < filtered_count; ++aidx) {
            const dg_trans_attachment *a = &filtered[aidx];
            dg_trans_slot_id slot_id = resolved[aidx];
            const dg_trans_slot *slot;
            dg_trans_slot_occupancy occ;

            if (slot_id == 0u) continue;
            if (!dg_trans_attachment_overlaps(a, s_begin, s_end)) continue;

            slot = dg_trans_section_find_slot_const(section, slot_id);
            if (!slot) continue;

            if (dg_trans_segment_slotmap_reserve(m, m->count + 1u) != 0) {
                rc = -6;
                break;
            }

            memset(&occ, 0, sizeof(occ));
            occ.slot_id = slot_id;
            occ.occupant_type_id = a->occupant_type_id;
            occ.occupant_instance_id = a->occupant_instance_id;
            occ.offset_t = (dg_q)d_q48_16_add((q48_16)slot->offset_t, (q48_16)a->local_t);
            occ.offset_h = (dg_q)d_q48_16_add((q48_16)slot->offset_h, (q48_16)a->local_h);
            m->items[m->count++] = occ;
        }

        if (rc != 0) break;
        dg_trans_occ_insertion_sort(m->items, m->count);
    }

    if (filtered) free(filtered);
    if (resolved) free(resolved);
    return rc;
}
