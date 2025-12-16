/*
FILE: source/domino/sim/sense/dg_observation_buffer.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sense/dg_observation_buffer
RESPONSIBILITY: Implements `dg_observation_buffer`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "sim/sense/dg_observation_buffer.h"

void dg_observation_buffer_init(dg_observation_buffer *b) {
    if (!b) {
        return;
    }
    b->tick = 0u;
    b->agent_id = 0u;
    b->records = (dg_observation_record *)0;
    b->count = 0u;
    b->capacity = 0u;
    b->arena = (unsigned char *)0;
    b->arena_cap = 0u;
    b->arena_used = 0u;
    b->owns_storage = D_FALSE;
    b->probe_refused_records = 0u;
    b->probe_refused_arena = 0u;
}

void dg_observation_buffer_free(dg_observation_buffer *b) {
    if (!b) {
        return;
    }
    if (b->owns_storage) {
        if (b->records) free(b->records);
        if (b->arena) free(b->arena);
    }
    dg_observation_buffer_init(b);
}

int dg_observation_buffer_reserve(dg_observation_buffer *b, u32 max_obs, u32 arena_bytes) {
    dg_observation_record *recs;
    unsigned char *arena;

    if (!b) {
        return -1;
    }
    dg_observation_buffer_free(b);
    if (max_obs == 0u && arena_bytes == 0u) {
        return 0;
    }

    if (max_obs != 0u) {
        recs = (dg_observation_record *)malloc(sizeof(dg_observation_record) * (size_t)max_obs);
        if (!recs) {
            return -2;
        }
        memset(recs, 0, sizeof(dg_observation_record) * (size_t)max_obs);
    } else {
        recs = (dg_observation_record *)0;
    }

    if (arena_bytes != 0u) {
        arena = (unsigned char *)malloc((size_t)arena_bytes);
        if (!arena) {
            if (recs) free(recs);
            return -3;
        }
        memset(arena, 0, (size_t)arena_bytes);
    } else {
        arena = (unsigned char *)0;
    }

    b->records = recs;
    b->capacity = max_obs;
    b->arena = arena;
    b->arena_cap = arena_bytes;
    b->arena_used = 0u;
    b->count = 0u;
    b->owns_storage = D_TRUE;
    b->probe_refused_records = 0u;
    b->probe_refused_arena = 0u;
    return 0;
}

void dg_observation_buffer_begin_tick(dg_observation_buffer *b, dg_tick tick, dg_agent_id agent_id) {
    if (!b) {
        return;
    }
    b->tick = tick;
    b->agent_id = agent_id;
    b->count = 0u;
    b->arena_used = 0u;
}

int dg_observation_buffer_push(dg_observation_buffer *b, const dg_pkt_observation *obs) {
    dg_observation_record *r;
    unsigned char *dst;
    u32 need;

    if (!b || !obs) {
        return -1;
    }
    if (!b->records || b->capacity == 0u) {
        b->probe_refused_records += 1u;
        return -2;
    }
    if (b->count >= b->capacity) {
        b->probe_refused_records += 1u;
        return -3;
    }
    if (obs->hdr.tick != b->tick) {
        return -4;
    }
    if (obs->payload_len != obs->hdr.payload_len) {
        return -5;
    }

    need = obs->payload_len;
    if (need != 0u) {
        if (!b->arena || b->arena_cap == 0u) {
            b->probe_refused_arena += 1u;
            return -6;
        }
        if (b->arena_used > b->arena_cap - need) {
            b->probe_refused_arena += 1u;
            return -7;
        }
        if (!obs->payload) {
            return -8;
        }
        dst = b->arena + b->arena_used;
        memcpy(dst, obs->payload, (size_t)need);
        b->arena_used += need;
    } else {
        dst = (unsigned char *)0;
    }

    r = &b->records[b->count];
    memset(r, 0, sizeof(*r));
    r->hdr = obs->hdr;
    r->payload = dst;
    r->payload_len = need;
    b->count += 1u;
    return 0;
}

static int dg_observation_record_cmp(const dg_observation_record *a, const dg_observation_record *b) {
    u32 min_len;
    int mc;

    if (a->hdr.type_id < b->hdr.type_id) return -1;
    if (a->hdr.type_id > b->hdr.type_id) return 1;

    if (a->hdr.src_entity < b->hdr.src_entity) return -1;
    if (a->hdr.src_entity > b->hdr.src_entity) return 1;

    if (a->hdr.seq < b->hdr.seq) return -1;
    if (a->hdr.seq > b->hdr.seq) return 1;

    if (a->hdr.schema_id < b->hdr.schema_id) return -1;
    if (a->hdr.schema_id > b->hdr.schema_id) return 1;

    if (a->hdr.schema_ver < b->hdr.schema_ver) return -1;
    if (a->hdr.schema_ver > b->hdr.schema_ver) return 1;

    if (a->hdr.dst_entity < b->hdr.dst_entity) return -1;
    if (a->hdr.dst_entity > b->hdr.dst_entity) return 1;

    if (a->hdr.domain_id < b->hdr.domain_id) return -1;
    if (a->hdr.domain_id > b->hdr.domain_id) return 1;

    if (a->hdr.chunk_id < b->hdr.chunk_id) return -1;
    if (a->hdr.chunk_id > b->hdr.chunk_id) return 1;

    if (a->payload_len < b->payload_len) return -1;
    if (a->payload_len > b->payload_len) return 1;

    min_len = (a->payload_len < b->payload_len) ? a->payload_len : b->payload_len;
    if (min_len != 0u) {
        mc = memcmp(a->payload, b->payload, (size_t)min_len);
        if (mc < 0) return -1;
        if (mc > 0) return 1;
    }

    return 0;
}

static int dg_observation_record_cmp_qsort(const void *pa, const void *pb) {
    const dg_observation_record *a = (const dg_observation_record *)pa;
    const dg_observation_record *b = (const dg_observation_record *)pb;
    return dg_observation_record_cmp(a, b);
}

void dg_observation_buffer_canonize(dg_observation_buffer *b) {
    if (!b || !b->records || b->count <= 1u) {
        return;
    }
    qsort(b->records, (size_t)b->count, sizeof(dg_observation_record), dg_observation_record_cmp_qsort);
}

u32 dg_observation_buffer_count(const dg_observation_buffer *b) {
    return b ? b->count : 0u;
}

const dg_observation_record *dg_observation_buffer_at(const dg_observation_buffer *b, u32 index) {
    if (!b || !b->records || index >= b->count) {
        return (const dg_observation_record *)0;
    }
    return &b->records[index];
}

u32 dg_observation_buffer_probe_refused_records(const dg_observation_buffer *b) {
    return b ? b->probe_refused_records : 0u;
}

u32 dg_observation_buffer_probe_refused_arena(const dg_observation_buffer *b) {
    return b ? b->probe_refused_arena : 0u;
}

