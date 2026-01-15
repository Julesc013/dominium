/*
FILE: source/domino/dknowledge.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dknowledge
RESPONSIBILITY: Implements `dknowledge`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dknowledge.h"

#include <string.h>

#define DKNOW_MAX_BASES   64
#define DKNOW_MAX_RECORDS 4096

static KnowledgeBase  g_bases[DKNOW_MAX_BASES];
static KnowledgeId    g_base_count = 0;
static KnowledgeRecord g_records_pool[DKNOW_MAX_RECORDS];
static U32             g_records_used = 0;

static Q16_16 dknow_clamp_q16(Q16_16 v, Q16_16 lo, Q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static KnowledgeRecord *dknow_alloc_records(U32 capacity)
{
    KnowledgeRecord *ptr;
    if (capacity == 0) return 0;
    if (g_records_used + capacity > DKNOW_MAX_RECORDS) return 0;
    ptr = &g_records_pool[g_records_used];
    g_records_used += capacity;
    memset(ptr, 0, sizeof(KnowledgeRecord) * capacity);
    return ptr;
}

KnowledgeId dknowledge_create(U32 capacity)
{
    KnowledgeBase *kb;
    if (g_base_count >= (KnowledgeId)DKNOW_MAX_BASES) return 0;
    kb = &g_bases[g_base_count];
    kb->records = dknow_alloc_records(capacity);
    if (!kb->records) return 0;
    kb->record_capacity = capacity;
    kb->record_count = 0;
    kb->id = ++g_base_count;
    return kb->id;
}

KnowledgeBase *dknowledge_get(KnowledgeId id)
{
    if (id == 0 || id > g_base_count) return 0;
    return &g_bases[id - 1];
}

void dknowledge_destroy(KnowledgeId id)
{
    KnowledgeBase *kb = dknowledge_get(id);
    if (!kb) return;
    kb->records = 0;
    kb->record_capacity = 0;
    kb->record_count = 0;
    kb->id = 0;
}

static int dknowledge_find_record(const KnowledgeBase *kb, const KnowledgeKey *key)
{
    U32 i;
    if (!kb || !key) return -1;
    for (i = 0; i < kb->record_count; ++i) {
        const KnowledgeRecord *r = &kb->records[i];
        if (r->key.type == key->type && r->key.subject_id == key->subject_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dknowledge_pick_replacement(KnowledgeBase *kb)
{
    U32 i;
    int idx = -1;
    Q16_16 best_conf = (Q16_16)(1 << 16);
    SimTick oldest_tick = (SimTick)(~(U64)0);
    if (!kb) return -1;
    for (i = 0; i < kb->record_capacity; ++i) {
        KnowledgeRecord *r = &kb->records[i];
        if (i >= kb->record_count) {
            return (int)i;
        }
        if (r->confidence_0_1 < best_conf) {
            best_conf = r->confidence_0_1;
            oldest_tick = r->last_seen_tick;
            idx = (int)i;
        } else if (r->confidence_0_1 == best_conf && r->last_seen_tick < oldest_tick) {
            oldest_tick = r->last_seen_tick;
            idx = (int)i;
        }
    }
    return idx;
}

void dknowledge_observe(KnowledgeId id,
                        const KnowledgeKey *key,
                        SimTick tick,
                        Q16_16 confidence)
{
    KnowledgeBase *kb = dknowledge_get(id);
    int idx;
    if (!kb || !key) return;
    confidence = dknow_clamp_q16(confidence, 0, (Q16_16)(1 << 16));
    idx = dknowledge_find_record(kb, key);
    if (idx >= 0) {
        KnowledgeRecord *r = &kb->records[idx];
        if (confidence > r->confidence_0_1) {
            r->confidence_0_1 = confidence;
        }
        r->last_seen_tick = tick;
        return;
    }
    idx = dknowledge_pick_replacement(kb);
    if (idx < 0) return;
    {
        KnowledgeRecord *r = &kb->records[idx];
        r->key = *key;
        r->last_seen_tick = tick;
        r->confidence_0_1 = confidence;
        if (idx >= (int)kb->record_count) {
            kb->record_count = idx + 1;
        }
    }
}

const KnowledgeRecord *dknowledge_query(const KnowledgeBase *kb,
                                        const KnowledgeKey *key)
{
    int idx;
    if (!kb || !key) return 0;
    idx = dknowledge_find_record(kb, key);
    if (idx < 0) return 0;
    return &kb->records[idx];
}

static uint32_t dknowledge_tile_subject(TileCoord x, TileCoord y, TileHeight z)
{
    uint32_t hx = (uint32_t)x & 0xFFFF;
    uint32_t hy = (uint32_t)y & 0xFFFF;
    uint32_t hz = ((uint32_t)z) & 0xFFF;
    return (hx << 16) ^ (hy << 4) ^ hz;
}

void dknowledge_mark_tile_visible(KnowledgeId id,
                                  TileCoord x,
                                  TileCoord y,
                                  TileHeight z,
                                  SimTick tick)
{
    KnowledgeKey key;
    key.type = KNOW_TILE_VISIBILITY;
    key.subject_id = dknowledge_tile_subject(x, y, z);
    dknowledge_observe(id, &key, tick, (Q16_16)(1 << 16));
}
