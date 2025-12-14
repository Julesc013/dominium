#include <stdio.h>
#include <string.h>

#include "res/dg_tlv_canon.h"

#include "sim/pkt/dg_pkt_common.h"

#include "sim/act/dg_delta_registry.h"
#include "sim/act/dg_delta_buffer.h"
#include "sim/act/dg_delta_commit.h"

#include "sim/sched/dg_sched.h"

#define TASSERT(cond, msg) do { \
    if (!(cond)) { \
        printf("FAIL: %s (line %u)\n", (msg), (unsigned int)__LINE__); \
        return 1; \
    } \
} while (0)

static u64 fnv1a64_bytes(u64 h, const unsigned char *data, u32 len) {
    u32 i;
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 fnv1a64_u64_le(u64 h, u64 v) {
    unsigned char buf[8];
    dg_le_write_u64(buf, v);
    return fnv1a64_bytes(h, buf, 8u);
}

/* --- 7.1 Delta commit order test --- */

typedef struct test_world_s {
    u64 applied_schema_ids[32];
    u32 applied_count;
} test_world;

static void test_delta_apply_record_schema(void *world, const dg_pkt_delta *delta) {
    test_world *w = (test_world *)world;
    if (!w || !delta) {
        return;
    }
    if (w->applied_count >= 32u) {
        return;
    }
    w->applied_schema_ids[w->applied_count++] = delta->hdr.schema_id;
}

static int test_delta_commit_order(void) {
    dg_delta_registry reg;
    dg_delta_handler_vtbl vtbl;
    dg_delta_buffer buf;
    dg_delta_commit_stats st;
    test_world w;
    const dg_tick tick = 5u;
    const dg_type_id delta_type = 1u;

    dg_pkt_delta deltas[6];
    dg_order_key keys[6];
    u64 ids[6];
    u32 i;

    /* Insertion order intentionally scrambled. */
    u32 ins_order[6] = { 3u, 1u, 5u, 0u, 4u, 2u };

    /* Expected canonical order by key:
     * (domain_id,chunk_id,entity_id,component_id,seq)
     * -> schema_id list: 102,105,101,104,100,103
     */
    u64 expected_ids[6] = { 102u, 105u, 101u, 104u, 100u, 103u };

    ids[0] = 100u;
    ids[1] = 101u;
    ids[2] = 102u;
    ids[3] = 103u;
    ids[4] = 104u;
    ids[5] = 105u;

    memset(&w, 0, sizeof(w));

    dg_delta_registry_init(&reg);
    vtbl.apply = test_delta_apply_record_schema;
    vtbl.estimate_cost = (u32 (*)(const dg_pkt_delta *))0;
    TASSERT(dg_delta_registry_add(&reg, delta_type, &vtbl, "test") == 0, "delta registry add failed");

    dg_delta_buffer_init(&buf);
    TASSERT(dg_delta_buffer_reserve(&buf, 16u, 0u) == 0, "delta buffer reserve failed");
    dg_delta_buffer_begin_tick(&buf, tick);

    /* Construct deltas + commit keys (same tick, same type; varying keys). */
    for (i = 0u; i < 6u; ++i) {
        dg_pkt_hdr hdr;
        dg_pkt_hdr_clear(&hdr);
        hdr.type_id = delta_type;
        hdr.schema_id = ids[i];
        hdr.schema_ver = 1u;
        hdr.flags = DG_PKT_FLAG_NONE;
        hdr.tick = tick;
        hdr.dst_entity = 0u;
        hdr.payload_len = 0u;

        if (i == 0u) { hdr.domain_id = 1u; hdr.chunk_id = 5u; hdr.src_entity = 2u; hdr.seq = 10u; keys[i] = dg_order_key_make((u16)DG_PH_COMMIT, 1u, 5u, 2u, 0u, delta_type, 10u); }
        if (i == 1u) { hdr.domain_id = 1u; hdr.chunk_id = 5u; hdr.src_entity = 1u; hdr.seq = 20u; keys[i] = dg_order_key_make((u16)DG_PH_COMMIT, 1u, 5u, 1u, 0u, delta_type, 20u); }
        if (i == 2u) { hdr.domain_id = 1u; hdr.chunk_id = 4u; hdr.src_entity = 9u; hdr.seq = 30u; keys[i] = dg_order_key_make((u16)DG_PH_COMMIT, 1u, 4u, 9u, 0u, delta_type, 30u); }
        if (i == 3u) { hdr.domain_id = 2u; hdr.chunk_id = 1u; hdr.src_entity = 1u; hdr.seq = 40u; keys[i] = dg_order_key_make((u16)DG_PH_COMMIT, 2u, 1u, 1u, 0u, delta_type, 40u); }
        if (i == 4u) { hdr.domain_id = 1u; hdr.chunk_id = 5u; hdr.src_entity = 1u; hdr.seq = 0u;  keys[i] = dg_order_key_make((u16)DG_PH_COMMIT, 1u, 5u, 1u, 1u, delta_type, 0u); }
        if (i == 5u) { hdr.domain_id = 1u; hdr.chunk_id = 5u; hdr.src_entity = 1u; hdr.seq = 0u;  keys[i] = dg_order_key_make((u16)DG_PH_COMMIT, 1u, 5u, 1u, 0u, delta_type, 0u); }

        deltas[i].hdr = hdr;
        deltas[i].payload = (const unsigned char *)0;
        deltas[i].payload_len = 0u;
    }

    for (i = 0u; i < 6u; ++i) {
        u32 idx = ins_order[i];
        TASSERT(dg_delta_buffer_push(&buf, &keys[idx], &deltas[idx]) == 0, "delta buffer push failed");
    }

    TASSERT(dg_delta_commit_apply(&w, &reg, &buf, &st) == 0, "delta commit apply failed");
    TASSERT(st.deltas_applied == 6u, "expected 6 deltas applied");
    TASSERT(st.deltas_rejected == 0u, "expected 0 deltas rejected");
    TASSERT(w.applied_count == 6u, "world applied count mismatch");

    {
        u64 got = 14695981039346656037ULL;
        u64 exp = 14695981039346656037ULL;
        for (i = 0u; i < 6u; ++i) {
            got = fnv1a64_u64_le(got, w.applied_schema_ids[i]);
            exp = fnv1a64_u64_le(exp, expected_ids[i]);
        }
        TASSERT(got == exp, "applied order list hash mismatch");
    }

    dg_delta_buffer_free(&buf);
    dg_delta_registry_free(&reg);
    return 0;
}

/* --- 7.2 Budget deferral determinism test --- */

typedef struct work_log_s {
    u64 processed_entity_ids[32];
    u32 count;
} work_log;

static void test_work_record_entity(struct dg_sched *sched, const dg_work_item *item, void *user_ctx) {
    work_log *log = (work_log *)user_ctx;
    (void)sched;
    if (!log || !item) {
        return;
    }
    if (log->count >= 32u) {
        return;
    }
    log->processed_entity_ids[log->count++] = item->key.entity_id;
}

static int run_deferral_case(const u32 *enqueue_order, u64 *out_proc, u32 *out_proc_n, u64 *out_rem, u32 *out_rem_n) {
    dg_sched s;
    work_log log;
    dg_work_item items[4];
    u32 i;

    memset(&log, 0, sizeof(log));
    dg_sched_init(&s);
    TASSERT(dg_sched_reserve(&s, 16u, 0u, 0u, 0u, 0u, 0u) == 0, "sched reserve failed");
    dg_sched_set_work_handler(&s, test_work_record_entity, &log);
    dg_sched_set_phase_budget_limit(&s, DG_PH_TOPOLOGY, 6u);

    for (i = 0u; i < 4u; ++i) {
        dg_work_item_clear(&items[i]);
        items[i].key = dg_order_key_make((u16)DG_PH_TOPOLOGY, 0u, 0u, (u64)(i + 1u), 0u, 0u, 0u);
        items[i].work_type_id = 1u;
        items[i].enqueue_tick = 1u;
        items[i].payload_ptr = (const unsigned char *)0;
        items[i].payload_len = 0u;
        items[i].payload_inline_len = 0u;
    }

    /* Costs are chosen to force "no skipping":
     * entity 1 cost 5 -> processed
     * entity 2 cost 10 -> blocks remaining, even though later items are cheaper
     */
    items[0].cost_units = 5u;  /* entity_id = 1 */
    items[1].cost_units = 10u; /* entity_id = 2 */
    items[2].cost_units = 1u;  /* entity_id = 3 */
    items[3].cost_units = 2u;  /* entity_id = 4 */

    for (i = 0u; i < 4u; ++i) {
        TASSERT(dg_sched_enqueue_work(&s, DG_PH_TOPOLOGY, &items[enqueue_order[i]]) == 0, "enqueue failed");
    }

    TASSERT(dg_sched_tick(&s, (void *)0, 1u) == 0, "sched tick failed");

    *out_proc_n = log.count;
    for (i = 0u; i < log.count; ++i) {
        out_proc[i] = log.processed_entity_ids[i];
    }

    {
        const dg_work_queue *q = &s.phase_queues[(u32)DG_PH_TOPOLOGY];
        u32 n = dg_work_queue_count(q);
        *out_rem_n = n;
        for (i = 0u; i < n; ++i) {
            const dg_work_item *it = dg_work_queue_at(q, i);
            TASSERT(it != (const dg_work_item *)0, "queue at");
            out_rem[i] = it->key.entity_id;
        }
    }

    dg_sched_free(&s);
    return 0;
}

static int test_budget_deferral_determinism(void) {
    u32 order_a[4] = { 2u, 0u, 3u, 1u };
    u32 order_b[4] = { 1u, 3u, 0u, 2u };
    u64 proc_a[32];
    u64 proc_b[32];
    u32 proc_an = 0u;
    u32 proc_bn = 0u;
    u64 rem_a[32];
    u64 rem_b[32];
    u32 rem_an = 0u;
    u32 rem_bn = 0u;
    u32 i;

    TASSERT(run_deferral_case(order_a, proc_a, &proc_an, rem_a, &rem_an) == 0, "case A failed");
    TASSERT(run_deferral_case(order_b, proc_b, &proc_bn, rem_b, &rem_bn) == 0, "case B failed");

    TASSERT(proc_an == proc_bn, "processed count mismatch");
    for (i = 0u; i < proc_an; ++i) {
        TASSERT(proc_a[i] == proc_b[i], "processed order mismatch");
    }

    TASSERT(rem_an == rem_bn, "remaining count mismatch");
    for (i = 0u; i < rem_an; ++i) {
        TASSERT(rem_a[i] == rem_b[i], "remaining queue mismatch");
    }

    /* Expect "no skipping": only entity 1 processed, others remain. */
    TASSERT(proc_an == 1u && proc_a[0] == 1u, "unexpected processed sequence");
    TASSERT(rem_an == 3u && rem_a[0] == 2u && rem_a[1] == 3u && rem_a[2] == 4u, "unexpected remaining sequence");
    return 0;
}

/* --- 7.3 Handler registry determinism test --- */

static void dummy_apply(void *world, const dg_pkt_delta *delta) {
    (void)world;
    (void)delta;
}

static int test_delta_registry_determinism(void) {
    dg_delta_registry ra;
    dg_delta_registry rb;
    dg_delta_handler_vtbl vtbl;
    dg_type_id type_ids[6] = { 50u, 10u, 200u, 3u, 99u, 1u };
    u32 order_a[6] = { 2u, 0u, 5u, 1u, 3u, 4u };
    u32 order_b[6] = { 4u, 3u, 1u, 5u, 0u, 2u };
    u32 i;
    u64 ha;
    u64 hb;

    dg_delta_registry_init(&ra);
    dg_delta_registry_init(&rb);

    vtbl.apply = dummy_apply;
    vtbl.estimate_cost = (u32 (*)(const dg_pkt_delta *))0;

    for (i = 0u; i < 6u; ++i) {
        TASSERT(dg_delta_registry_add(&ra, type_ids[order_a[i]], &vtbl, "a") == 0, "registry add A failed");
    }
    for (i = 0u; i < 6u; ++i) {
        TASSERT(dg_delta_registry_add(&rb, type_ids[order_b[i]], &vtbl, "b") == 0, "registry add B failed");
    }

    TASSERT(dg_delta_registry_count(&ra) == 6u, "registry count A");
    TASSERT(dg_delta_registry_count(&rb) == 6u, "registry count B");

    ha = 14695981039346656037ULL;
    hb = 14695981039346656037ULL;
    for (i = 0u; i < 6u; ++i) {
        const dg_delta_registry_entry *ea = dg_delta_registry_at(&ra, i);
        const dg_delta_registry_entry *eb = dg_delta_registry_at(&rb, i);
        TASSERT(ea && eb, "registry at");
        TASSERT(ea->type_id == eb->type_id, "type_id mismatch");
        if (i > 0u) {
            const dg_delta_registry_entry *prev = dg_delta_registry_at(&ra, i - 1u);
            TASSERT(prev, "registry prev");
            TASSERT(prev->type_id < ea->type_id, "type_id ordering violated");
        }
        ha = fnv1a64_u64_le(ha, (u64)ea->type_id);
        hb = fnv1a64_u64_le(hb, (u64)eb->type_id);
    }
    TASSERT(ha == hb, "registry aggregate hash mismatch");

    dg_delta_registry_free(&ra);
    dg_delta_registry_free(&rb);
    return 0;
}

int main(void) {
    TASSERT(test_delta_commit_order() == 0, "delta commit order");
    TASSERT(test_budget_deferral_determinism() == 0, "budget deferral determinism");
    TASSERT(test_delta_registry_determinism() == 0, "delta registry determinism");
    printf("OK: sched_determinism_test\n");
    return 0;
}

