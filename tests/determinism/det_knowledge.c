#include "det_common.h"

#include "domino/dknowledge.h"

static int det_know_key_cmp(const KnowledgeKey *a, const KnowledgeKey *b) {
    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    if ((u32)a->type < (u32)b->type) return -1;
    if ((u32)a->type > (u32)b->type) return 1;
    if (a->subject_id < b->subject_id) return -1;
    if (a->subject_id > b->subject_id) return 1;
    return 0;
}

static void det_know_sort_records(KnowledgeRecord *recs, u32 n) {
    u32 i;
    if (!recs) return;
    for (i = 1u; i < n; ++i) {
        KnowledgeRecord key = recs[i];
        u32 j = i;
        while (j > 0u && det_know_key_cmp(&recs[j - 1u].key, &key.key) > 0) {
            recs[j] = recs[j - 1u];
            --j;
        }
        recs[j] = key;
    }
}

static u64 det_know_hash_canon(const KnowledgeBase *kb) {
    KnowledgeRecord tmp[32];
    u32 n;
    u32 i;
    u64 h = 0xBEEFBEEFBEEFBEEFULL;

    if (!kb || !kb->records) {
        return 0u;
    }

    n = (kb->record_count > 32u) ? 32u : kb->record_count;
    for (i = 0u; i < n; ++i) {
        tmp[i] = kb->records[i];
    }
    det_know_sort_records(tmp, n);

    h = det_hash_step_u64(h, (u64)n);
    for (i = 0u; i < n; ++i) {
        h = det_hash_step_u64(h, (u64)tmp[i].key.type);
        h = det_hash_step_u64(h, (u64)tmp[i].key.subject_id);
        h = det_hash_step_u64(h, (u64)tmp[i].last_seen_tick);
        h = det_hash_step_i64(h, (i64)tmp[i].confidence_0_1);
    }
    return h;
}

static u64 det_know_run_case(int variant) {
    KnowledgeId id;
    KnowledgeBase *kb;
    KnowledgeKey keys[6];
    u32 order_a[6] = { 0u, 1u, 2u, 3u, 4u, 5u };
    u32 order_b[6] = { 5u, 2u, 4u, 1u, 3u, 0u };
    u32 i;
    const u32 *order = (variant == 0) ? order_a : order_b;

    id = dknowledge_create(16u);
    DET_ASSERT(id != 0u);
    kb = dknowledge_get(id);
    DET_ASSERT(kb != (KnowledgeBase *)0);

    keys[0].type = KNOW_TILE_VISIBILITY; keys[0].subject_id = 0x00010002u;
    keys[1].type = KNOW_TILE_VISIBILITY; keys[1].subject_id = 0x00010003u;
    keys[2].type = KNOW_ENTITY_SEEN; keys[2].subject_id = 42u;
    keys[3].type = KNOW_ENTITY_SEEN; keys[3].subject_id = 7u;
    keys[4].type = KNOW_MARKET_INFO; keys[4].subject_id = 100u;
    keys[5].type = KNOW_MARKET_INFO; keys[5].subject_id = 101u;

    for (i = 0u; i < 6u; ++i) {
        u32 idx = order[i];
        dknowledge_observe(id, &keys[idx], (SimTick)10u, (Q16_16)(1 << 16));
    }

    return det_know_hash_canon(kb);
}

int main(void) {
    u64 ha;
    u64 hb;
    ha = det_know_run_case(0);
    hb = det_know_run_case(1);
    DET_ASSERT(ha == hb);
    return 0;
}

