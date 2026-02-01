/*
FILE: tests/domino_trans/test_dg_trans_compile_determinism.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_trans
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "core/dg_det_hash.h"

#include "trans/model/dg_trans_alignment.h"
#include "trans/model/dg_trans_section.h"
#include "trans/model/dg_trans_attachment.h"
#include "trans/model/dg_trans_junction.h"

#include "trans/compile/dg_trans_compile.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

#define QONE ((dg_q)((i64)1 << 16))

static dg_q q_int(i64 v) { return (dg_q)(v * (i64)QONE); }

static dg_vec3_q v3(dg_q x, dg_q y, dg_q z) {
    dg_vec3_q v;
    v.x = x; v.y = y; v.z = z;
    return v;
}

static const dg_trans_compiled_alignment *find_compiled_alignment(const dg_trans_compiler *c, dg_trans_alignment_id id) {
    u32 i;
    if (!c) return (const dg_trans_compiled_alignment *)0;
    for (i = 0u; i < c->compiled.alignment_count; ++i) {
        if (c->compiled.alignments[i].alignment_id == id) {
            return &c->compiled.alignments[i];
        }
    }
    return (const dg_trans_compiled_alignment *)0;
}

static u64 hash_step_u64(u64 h, u64 v) { return dg_det_hash_u64(h ^ v); }
static u64 hash_step_i64(u64 h, i64 v) { return dg_det_hash_u64(h ^ (u64)v); }

static u64 hash_alignment_compiled(const dg_trans_compiled_alignment *ca) {
    u64 h = 0xA5A5A5A5A5A5A5A5ULL;
    u32 i;
    if (!ca) return 0u;

    h = hash_step_u64(h, (u64)ca->alignment_id);
    h = hash_step_i64(h, (i64)ca->last_length_q);
    h = hash_step_u64(h, (u64)ca->seg_count);

    for (i = 0u; i < ca->seg_count; ++i) {
        const dg_trans_microseg *s = &ca->segs[i];
        const dg_trans_segment_slotmap *m = &ca->slotmaps[i];
        u32 j;

        h = hash_step_u64(h, (u64)s->id.alignment_id);
        h = hash_step_u64(h, (u64)s->id.segment_index);
        h = hash_step_i64(h, (i64)s->s_begin);
        h = hash_step_i64(h, (i64)s->s_end);
        h = hash_step_i64(h, (i64)s->bbox.min.x);
        h = hash_step_i64(h, (i64)s->bbox.min.y);
        h = hash_step_i64(h, (i64)s->bbox.min.z);
        h = hash_step_i64(h, (i64)s->bbox.max.x);
        h = hash_step_i64(h, (i64)s->bbox.max.y);
        h = hash_step_i64(h, (i64)s->bbox.max.z);

        h = hash_step_i64(h, (i64)s->frame0.origin.x);
        h = hash_step_i64(h, (i64)s->frame0.origin.y);
        h = hash_step_i64(h, (i64)s->frame0.origin.z);
        h = hash_step_i64(h, (i64)s->frame0.forward.x);
        h = hash_step_i64(h, (i64)s->frame0.forward.y);
        h = hash_step_i64(h, (i64)s->frame0.forward.z);
        h = hash_step_i64(h, (i64)s->frame0.right.x);
        h = hash_step_i64(h, (i64)s->frame0.right.y);
        h = hash_step_i64(h, (i64)s->frame0.right.z);
        h = hash_step_i64(h, (i64)s->frame0.up.x);
        h = hash_step_i64(h, (i64)s->frame0.up.y);
        h = hash_step_i64(h, (i64)s->frame0.up.z);

        h = hash_step_u64(h, (u64)m->count);
        for (j = 0u; j < m->count; ++j) {
            const dg_trans_slot_occupancy *o = &m->items[j];
            h = hash_step_u64(h, (u64)o->slot_id);
            h = hash_step_u64(h, (u64)o->occupant_type_id);
            h = hash_step_u64(h, (u64)o->occupant_instance_id);
            h = hash_step_i64(h, (i64)o->offset_t);
            h = hash_step_i64(h, (i64)o->offset_h);
        }
    }

    return h;
}

static int compiled_alignment_eq(const dg_trans_compiled_alignment *a, const dg_trans_compiled_alignment *b) {
    u32 i;
    if (!a || !b) return 0;
    if (a->alignment_id != b->alignment_id) return 0;
    if (a->seg_count != b->seg_count) return 0;

    for (i = 0u; i < a->seg_count; ++i) {
        const dg_trans_microseg *sa = &a->segs[i];
        const dg_trans_microseg *sb = &b->segs[i];
        const dg_trans_segment_slotmap *ma = &a->slotmaps[i];
        const dg_trans_segment_slotmap *mb = &b->slotmaps[i];
        u32 j;

        if (sa->id.alignment_id != sb->id.alignment_id) return 0;
        if (sa->id.segment_index != sb->id.segment_index) return 0;
        if (sa->s_begin != sb->s_begin) return 0;
        if (sa->s_end != sb->s_end) return 0;
        if (sa->bbox.min.x != sb->bbox.min.x) return 0;
        if (sa->bbox.min.y != sb->bbox.min.y) return 0;
        if (sa->bbox.min.z != sb->bbox.min.z) return 0;
        if (sa->bbox.max.x != sb->bbox.max.x) return 0;
        if (sa->bbox.max.y != sb->bbox.max.y) return 0;
        if (sa->bbox.max.z != sb->bbox.max.z) return 0;

        if (sa->frame0.origin.x != sb->frame0.origin.x) return 0;
        if (sa->frame0.origin.y != sb->frame0.origin.y) return 0;
        if (sa->frame0.origin.z != sb->frame0.origin.z) return 0;
        if (sa->frame0.forward.x != sb->frame0.forward.x) return 0;
        if (sa->frame0.forward.y != sb->frame0.forward.y) return 0;
        if (sa->frame0.forward.z != sb->frame0.forward.z) return 0;
        if (sa->frame0.right.x != sb->frame0.right.x) return 0;
        if (sa->frame0.right.y != sb->frame0.right.y) return 0;
        if (sa->frame0.right.z != sb->frame0.right.z) return 0;
        if (sa->frame0.up.x != sb->frame0.up.x) return 0;
        if (sa->frame0.up.y != sb->frame0.up.y) return 0;
        if (sa->frame0.up.z != sb->frame0.up.z) return 0;

        if (ma->count != mb->count) return 0;
        for (j = 0u; j < ma->count; ++j) {
            const dg_trans_slot_occupancy *oa = &ma->items[j];
            const dg_trans_slot_occupancy *ob = &mb->items[j];
            if (oa->slot_id != ob->slot_id) return 0;
            if (oa->occupant_type_id != ob->occupant_type_id) return 0;
            if (oa->occupant_instance_id != ob->occupant_instance_id) return 0;
            if (oa->offset_t != ob->offset_t) return 0;
            if (oa->offset_h != ob->offset_h) return 0;
        }
    }
    return 1;
}

static void build_section_basic(dg_trans_section_archetype *sec, dg_trans_section_archetype_id id) {
    dg_trans_slot slot;
    dg_trans_occupant_type_id types_all[2];

    dg_trans_section_init(sec);
    sec->id = id;

    types_all[0] = 1u;
    types_all[1] = 2u;

    memset(&slot, 0, sizeof(slot));
    slot.slot_id = 1u;
    slot.offset_t = q_int(-1);
    slot.offset_h = 0;
    slot.width = q_int(1);
    slot.height = q_int(1);
    slot.allowed_types = types_all;
    slot.allowed_type_count = 2u;
    (void)dg_trans_section_set_slot(sec, &slot);

    memset(&slot, 0, sizeof(slot));
    slot.slot_id = 2u;
    slot.offset_t = 0;
    slot.offset_h = 0;
    slot.width = q_int(1);
    slot.height = q_int(1);
    slot.allowed_types = types_all;
    slot.allowed_type_count = 2u;
    (void)dg_trans_section_set_slot(sec, &slot);

    memset(&slot, 0, sizeof(slot));
    slot.slot_id = 3u;
    slot.offset_t = q_int(1);
    slot.offset_h = 0;
    slot.width = q_int(1);
    slot.height = q_int(1);
    slot.allowed_types = types_all;
    slot.allowed_type_count = 2u;
    (void)dg_trans_section_set_slot(sec, &slot);
}

static void build_alignment_poly(dg_trans_alignment *a, dg_trans_alignment_id id, dg_trans_section_archetype_id sec_id, const u32 *ins_order, u32 ins_count) {
    /* Control points are defined by stable point_index keys; insertion order may be arbitrary. */
    const u32 point_ids[4] = { 10u, 20u, 30u, 40u };
    dg_vec3_q point_pos[4];
    u32 i;

    dg_trans_alignment_init(a);
    a->id = id;
    a->section_id = sec_id;

    point_pos[0] = v3(0, 0, 0);
    point_pos[1] = v3(q_int(10), 0, 0);
    point_pos[2] = v3(q_int(20), 0, 0);
    point_pos[3] = v3(q_int(32), 0, 0);

    for (i = 0u; i < ins_count; ++i) {
        u32 idx = ins_order[i];
        (void)dg_trans_alignment_set_point(a, point_ids[idx], point_pos[idx]);
    }
}

static void mark_full_dirty(dg_trans_compiler *c, const dg_trans_alignment *a) {
    dg_q len;
    (void)dg_trans_alignment_length_q(a, &len);
    dg_trans_dirty_mark_alignment_microseg(&c->dirty, a->id, 0, len);
    dg_trans_dirty_mark_alignment_slotmap(&c->dirty, a->id, 0, len);
}

static void compile_until_done(dg_trans_compiler *c, const dg_trans_compile_input *in, u32 budget_units) {
    while (dg_trans_compiler_pending_work(c) != 0u) {
        (void)dg_trans_compiler_process(c, in, 1u, budget_units);
        if (budget_units != 0xFFFFFFFFu && budget_units == 0u) {
            break;
        }
    }
}

static int test_canonical_compilation_determinism(void) {
    dg_trans_section_archetype sec1;
    dg_trans_section_archetype sec2;
    dg_trans_alignment a1;
    dg_trans_alignment a2;
    dg_trans_attachment att1[3];
    dg_trans_attachment att2[3];
    dg_trans_compile_input in1;
    dg_trans_compile_input in2;
    dg_trans_compiler c1;
    dg_trans_compiler c2;
    const dg_trans_compiled_alignment *ca1;
    const dg_trans_compiled_alignment *ca2;
    u64 h1;
    u64 h2;
    u32 order_a[4] = { 0u, 1u, 2u, 3u };
    u32 order_b[4] = { 2u, 0u, 3u, 1u };

    build_section_basic(&sec1, 200u);
    build_section_basic(&sec2, 200u);
    build_alignment_poly(&a1, 100u, sec1.id, order_a, 4u);
    build_alignment_poly(&a2, 100u, sec2.id, order_b, 4u);

    memset(att1, 0, sizeof(att1));
    dg_trans_attachment_clear(&att1[0]);
    att1[0].alignment_id = a1.id;
    att1[0].occupant_type_id = 1u;
    att1[0].occupant_instance_id = 101u;
    att1[0].slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
    att1[0].s0 = 0;
    att1[0].s1 = q_int(32);

    dg_trans_attachment_clear(&att1[1]);
    att1[1].alignment_id = a1.id;
    att1[1].occupant_type_id = 1u;
    att1[1].occupant_instance_id = 102u;
    att1[1].slot.kind = DG_TRANS_SLOT_ASSIGN_EXPLICIT;
    att1[1].slot.slot_id = 2u;
    att1[1].s0 = q_int(5);
    att1[1].s1 = q_int(25);

    dg_trans_attachment_clear(&att1[2]);
    att1[2].alignment_id = a1.id;
    att1[2].occupant_type_id = 2u;
    att1[2].occupant_instance_id = 201u;
    att1[2].slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
    att1[2].s0 = 0;
    att1[2].s1 = q_int(32);

    /* Reordered insertion for attachments. */
    memset(att2, 0, sizeof(att2));
    att2[0] = att1[2];
    att2[1] = att1[0];
    att2[2] = att1[1];

    memset(&in1, 0, sizeof(in1));
    in1.alignments = &a1;
    in1.alignment_count = 1u;
    in1.sections = &sec1;
    in1.section_count = 1u;
    in1.attachments = att1;
    in1.attachment_count = 3u;
    in1.junctions = (const dg_trans_junction *)0;
    in1.junction_count = 0u;

    memset(&in2, 0, sizeof(in2));
    in2.alignments = &a2;
    in2.alignment_count = 1u;
    in2.sections = &sec2;
    in2.section_count = 1u;
    in2.attachments = att2;
    in2.attachment_count = 3u;
    in2.junctions = (const dg_trans_junction *)0;
    in2.junction_count = 0u;

    dg_trans_compiler_init(&c1);
    dg_trans_compiler_init(&c2);
    TEST_ASSERT(dg_trans_compiler_reserve(&c1, 64u, 1024u) == 0);
    TEST_ASSERT(dg_trans_compiler_reserve(&c2, 64u, 1024u) == 0);
    TEST_ASSERT(dg_trans_compiler_set_params(&c1, q_int(5), q_int(16)) == 0);
    TEST_ASSERT(dg_trans_compiler_set_params(&c2, q_int(5), q_int(16)) == 0);
    TEST_ASSERT(dg_trans_compiler_sync(&c1, &in1) == 0);
    TEST_ASSERT(dg_trans_compiler_sync(&c2, &in2) == 0);

    mark_full_dirty(&c1, &a1);
    mark_full_dirty(&c2, &a2);
    TEST_ASSERT(dg_trans_compiler_enqueue_dirty(&c1, 1u) == 0);
    TEST_ASSERT(dg_trans_compiler_enqueue_dirty(&c2, 1u) == 0);
    compile_until_done(&c1, &in1, 0xFFFFFFFFu);
    compile_until_done(&c2, &in2, 0xFFFFFFFFu);
    TEST_ASSERT(dg_trans_compiler_check_invariants(&c1, &in1) == 0);
    TEST_ASSERT(dg_trans_compiler_check_invariants(&c2, &in2) == 0);

    ca1 = find_compiled_alignment(&c1, a1.id);
    ca2 = find_compiled_alignment(&c2, a2.id);
    TEST_ASSERT(ca1 != (const dg_trans_compiled_alignment *)0);
    TEST_ASSERT(ca2 != (const dg_trans_compiled_alignment *)0);
    TEST_ASSERT(compiled_alignment_eq(ca1, ca2) != 0);

    h1 = hash_alignment_compiled(ca1);
    h2 = hash_alignment_compiled(ca2);
    TEST_ASSERT(h1 == h2);

    dg_trans_compiler_free(&c1);
    dg_trans_compiler_free(&c2);
    dg_trans_alignment_free(&a1);
    dg_trans_alignment_free(&a2);
    dg_trans_section_free(&sec1);
    dg_trans_section_free(&sec2);
    return 0;
}

static int test_dirty_range_compile_determinism(void) {
    dg_trans_section_archetype sec;
    dg_trans_alignment a;
    dg_trans_attachment atts[2];
    dg_trans_compile_input in;
    dg_trans_compiler partial;
    dg_trans_compiler full;
    const dg_trans_compiled_alignment *ca_partial;
    const dg_trans_compiled_alignment *ca_full;
    u64 h_partial;
    u64 h_full;
    dg_trans_dirty_alignment drec;
    u32 seg0, seg1;
    dg_q len;

    /* Build baseline authoring. */
    build_section_basic(&sec, 300u);
    {
        const u32 order[4] = { 0u, 1u, 2u, 3u };
        build_alignment_poly(&a, 111u, sec.id, order, 4u);
    }

    memset(atts, 0, sizeof(atts));
    dg_trans_attachment_clear(&atts[0]);
    atts[0].alignment_id = a.id;
    atts[0].occupant_type_id = 1u;
    atts[0].occupant_instance_id = 1u;
    atts[0].slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
    atts[0].s0 = 0;
    atts[0].s1 = q_int(32);

    dg_trans_attachment_clear(&atts[1]);
    atts[1].alignment_id = a.id;
    atts[1].occupant_type_id = 1u;
    atts[1].occupant_instance_id = 2u;
    atts[1].slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
    atts[1].s0 = 0;
    atts[1].s1 = q_int(32);

    memset(&in, 0, sizeof(in));
    in.alignments = &a;
    in.alignment_count = 1u;
    in.sections = &sec;
    in.section_count = 1u;
    in.attachments = atts;
    in.attachment_count = 2u;
    in.junctions = (const dg_trans_junction *)0;
    in.junction_count = 0u;

    /* Baseline compile in 'partial' compiler so it has carryover state. */
    dg_trans_compiler_init(&partial);
    TEST_ASSERT(dg_trans_compiler_reserve(&partial, 64u, 1024u) == 0);
    TEST_ASSERT(dg_trans_compiler_set_params(&partial, q_int(5), q_int(16)) == 0);
    TEST_ASSERT(dg_trans_compiler_sync(&partial, &in) == 0);
    mark_full_dirty(&partial, &a);
    TEST_ASSERT(dg_trans_compiler_enqueue_dirty(&partial, 1u) == 0);
    compile_until_done(&partial, &in, 0xFFFFFFFFu);
    TEST_ASSERT(dg_trans_compiler_pending_work(&partial) == 0u);
    TEST_ASSERT(dg_trans_compiler_check_invariants(&partial, &in) == 0);

    /* Modify a control point in the mid-to-end region (affects station >= 10m). */
    TEST_ASSERT(dg_trans_alignment_set_point(&a, 30u, v3(q_int(20), q_int(1), 0)) >= 0);

    /* Mark only the affected station range dirty (10m .. end). */
    (void)dg_trans_alignment_length_q(&a, &len);
    dg_trans_dirty_mark_alignment_microseg(&partial.dirty, a.id, q_int(10), len);
    dg_trans_dirty_mark_alignment_slotmap(&partial.dirty, a.id, q_int(10), len);

    /* Verify dirty range maps to a subset of segments. */
    TEST_ASSERT(dg_trans_dirty_get_alignment(&partial.dirty, a.id, &drec) == 1);
    TEST_ASSERT(drec.microseg.dirty == D_TRUE);
    TEST_ASSERT(dg_trans_dirty_range_to_seg_span(drec.microseg.s0, drec.microseg.s1, partial.microseg_max_len_q, &seg0, &seg1) == 0);
    TEST_ASSERT(seg0 == 2u);
    TEST_ASSERT(seg1 == 6u);

    /* Enqueue and process under constrained budget (forces carryover). */
    TEST_ASSERT(dg_trans_compiler_enqueue_dirty(&partial, 2u) == 0);
    TEST_ASSERT(dg_trans_compiler_pending_work(&partial) != 0u);
    (void)dg_trans_compiler_process(&partial, &in, 2u, 6u); /* enough for one range item, not both */
    TEST_ASSERT(dg_trans_compiler_pending_work(&partial) != 0u);
    compile_until_done(&partial, &in, 0xFFFFFFFFu);
    TEST_ASSERT(dg_trans_compiler_pending_work(&partial) == 0u);
    TEST_ASSERT(dg_trans_compiler_check_invariants(&partial, &in) == 0);

    /* Full compile from scratch after the same modification. */
    dg_trans_compiler_init(&full);
    TEST_ASSERT(dg_trans_compiler_reserve(&full, 64u, 1024u) == 0);
    TEST_ASSERT(dg_trans_compiler_set_params(&full, q_int(5), q_int(16)) == 0);
    TEST_ASSERT(dg_trans_compiler_sync(&full, &in) == 0);
    mark_full_dirty(&full, &a);
    TEST_ASSERT(dg_trans_compiler_enqueue_dirty(&full, 2u) == 0);
    compile_until_done(&full, &in, 0xFFFFFFFFu);
    TEST_ASSERT(dg_trans_compiler_check_invariants(&full, &in) == 0);

    ca_partial = find_compiled_alignment(&partial, a.id);
    ca_full = find_compiled_alignment(&full, a.id);
    TEST_ASSERT(ca_partial != (const dg_trans_compiled_alignment *)0);
    TEST_ASSERT(ca_full != (const dg_trans_compiled_alignment *)0);
    TEST_ASSERT(compiled_alignment_eq(ca_partial, ca_full) != 0);

    h_partial = hash_alignment_compiled(ca_partial);
    h_full = hash_alignment_compiled(ca_full);
    TEST_ASSERT(h_partial == h_full);

    dg_trans_compiler_free(&partial);
    dg_trans_compiler_free(&full);
    dg_trans_alignment_free(&a);
    dg_trans_section_free(&sec);
    return 0;
}

static int test_slot_packing_determinism(void) {
    dg_trans_section_archetype sec1;
    dg_trans_section_archetype sec2;
    dg_trans_alignment a1;
    dg_trans_alignment a2;
    dg_trans_attachment atts1[3];
    dg_trans_attachment atts2[3];
    dg_trans_compile_input in1;
    dg_trans_compile_input in2;
    dg_trans_compiler c1;
    dg_trans_compiler c2;
    const dg_trans_compiled_alignment *ca1;
    const dg_trans_compiled_alignment *ca2;
    u64 h1;
    u64 h2;
    const u32 order[4] = { 0u, 1u, 2u, 3u };

    build_section_basic(&sec1, 400u);
    build_section_basic(&sec2, 400u);
    build_alignment_poly(&a1, 500u, sec1.id, order, 4u);
    build_alignment_poly(&a2, 500u, sec2.id, order, 4u);

    memset(atts1, 0, sizeof(atts1));
    dg_trans_attachment_clear(&atts1[0]);
    atts1[0].alignment_id = a1.id;
    atts1[0].occupant_type_id = 1u;
    atts1[0].occupant_instance_id = 1u;
    atts1[0].slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
    atts1[0].s0 = 0;
    atts1[0].s1 = q_int(32);

    dg_trans_attachment_clear(&atts1[1]);
    atts1[1].alignment_id = a1.id;
    atts1[1].occupant_type_id = 1u;
    atts1[1].occupant_instance_id = 2u;
    atts1[1].slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
    atts1[1].s0 = 0;
    atts1[1].s1 = q_int(32);

    dg_trans_attachment_clear(&atts1[2]);
    atts1[2].alignment_id = a1.id;
    atts1[2].occupant_type_id = 1u;
    atts1[2].occupant_instance_id = 3u;
    atts1[2].slot.kind = DG_TRANS_SLOT_ASSIGN_AUTO;
    atts1[2].s0 = 0;
    atts1[2].s1 = q_int(32);

    /* Reordered insertion order; resolver should remain stable. */
    atts2[0] = atts1[2];
    atts2[1] = atts1[0];
    atts2[2] = atts1[1];

    memset(&in1, 0, sizeof(in1));
    in1.alignments = &a1;
    in1.alignment_count = 1u;
    in1.sections = &sec1;
    in1.section_count = 1u;
    in1.attachments = atts1;
    in1.attachment_count = 3u;
    in1.junctions = (const dg_trans_junction *)0;
    in1.junction_count = 0u;

    memset(&in2, 0, sizeof(in2));
    in2.alignments = &a2;
    in2.alignment_count = 1u;
    in2.sections = &sec2;
    in2.section_count = 1u;
    in2.attachments = atts2;
    in2.attachment_count = 3u;
    in2.junctions = (const dg_trans_junction *)0;
    in2.junction_count = 0u;

    dg_trans_compiler_init(&c1);
    dg_trans_compiler_init(&c2);
    TEST_ASSERT(dg_trans_compiler_reserve(&c1, 64u, 1024u) == 0);
    TEST_ASSERT(dg_trans_compiler_reserve(&c2, 64u, 1024u) == 0);
    TEST_ASSERT(dg_trans_compiler_set_params(&c1, q_int(8), q_int(16)) == 0);
    TEST_ASSERT(dg_trans_compiler_set_params(&c2, q_int(8), q_int(16)) == 0);
    TEST_ASSERT(dg_trans_compiler_sync(&c1, &in1) == 0);
    TEST_ASSERT(dg_trans_compiler_sync(&c2, &in2) == 0);

    mark_full_dirty(&c1, &a1);
    mark_full_dirty(&c2, &a2);
    TEST_ASSERT(dg_trans_compiler_enqueue_dirty(&c1, 1u) == 0);
    TEST_ASSERT(dg_trans_compiler_enqueue_dirty(&c2, 1u) == 0);
    compile_until_done(&c1, &in1, 0xFFFFFFFFu);
    compile_until_done(&c2, &in2, 0xFFFFFFFFu);
    TEST_ASSERT(dg_trans_compiler_check_invariants(&c1, &in1) == 0);
    TEST_ASSERT(dg_trans_compiler_check_invariants(&c2, &in2) == 0);

    ca1 = find_compiled_alignment(&c1, a1.id);
    ca2 = find_compiled_alignment(&c2, a2.id);
    TEST_ASSERT(ca1 != (const dg_trans_compiled_alignment *)0);
    TEST_ASSERT(ca2 != (const dg_trans_compiled_alignment *)0);
    TEST_ASSERT(compiled_alignment_eq(ca1, ca2) != 0);

    h1 = hash_alignment_compiled(ca1);
    h2 = hash_alignment_compiled(ca2);
    TEST_ASSERT(h1 == h2);

    dg_trans_compiler_free(&c1);
    dg_trans_compiler_free(&c2);
    dg_trans_alignment_free(&a1);
    dg_trans_alignment_free(&a2);
    dg_trans_section_free(&sec1);
    dg_trans_section_free(&sec2);
    return 0;
}

int main(void) {
    int rc;
    rc = test_canonical_compilation_determinism();
    if (rc != 0) return rc;
    rc = test_dirty_range_compile_determinism();
    if (rc != 0) return rc;
    rc = test_slot_packing_determinism();
    if (rc != 0) return rc;
    return 0;
}
