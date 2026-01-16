/*
FILE: source/domino/sim/act/dg_delta_buffer.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/act/dg_delta_buffer
RESPONSIBILITY: Implements `dg_delta_buffer`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "sim/act/dg_delta_buffer.h"

void dg_delta_buffer_init(dg_delta_buffer *b) {
    if (!b) {
        return;
    }
    b->tick = 0u;
    b->records = (dg_delta_record *)0;
    b->count = 0u;
    b->capacity = 0u;
    b->arena = (unsigned char *)0;
    b->arena_cap = 0u;
    b->arena_used = 0u;
    b->owns_storage = D_FALSE;
    b->probe_refused_records = 0u;
    b->probe_refused_arena = 0u;
}

void dg_delta_buffer_free(dg_delta_buffer *b) {
    if (!b) {
        return;
    }
    if (b->owns_storage) {
        if (b->records) free(b->records);
        if (b->arena) free(b->arena);
    }
    dg_delta_buffer_init(b);
}

int dg_delta_buffer_reserve(dg_delta_buffer *b, u32 max_deltas, u32 arena_bytes) {
    dg_delta_record *recs;
    unsigned char *arena;
    if (!b) {
        return -1;
    }
    dg_delta_buffer_free(b);
    if (max_deltas == 0u && arena_bytes == 0u) {
        return 0;
    }

    if (max_deltas != 0u) {
        recs = (dg_delta_record *)malloc(sizeof(dg_delta_record) * (size_t)max_deltas);
        if (!recs) {
            return -2;
        }
        memset(recs, 0, sizeof(dg_delta_record) * (size_t)max_deltas);
    } else {
        recs = (dg_delta_record *)0;
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
    b->capacity = max_deltas;
    b->arena = arena;
    b->arena_cap = arena_bytes;
    b->arena_used = 0u;
    b->count = 0u;
    b->owns_storage = D_TRUE;
    b->probe_refused_records = 0u;
    b->probe_refused_arena = 0u;
    return 0;
}

void dg_delta_buffer_begin_tick(dg_delta_buffer *b, dg_tick tick) {
    if (!b) {
        return;
    }
    b->tick = tick;
    b->count = 0u;
    b->arena_used = 0u;
}

int dg_delta_buffer_push(dg_delta_buffer *b, const dg_order_key *key, const dg_pkt_delta *delta) {
    dg_delta_record *r;
    unsigned char *dst;
    u32 need;

    if (!b || !key || !delta) {
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
    if (delta->hdr.tick != b->tick) {
        return -4;
    }
    if (delta->payload_len != delta->hdr.payload_len) {
        return -5;
    }

    need = delta->payload_len;
    if (need != 0u) {
        if (!b->arena || b->arena_cap == 0u) {
            b->probe_refused_arena += 1u;
            return -6;
        }
        if (b->arena_used > b->arena_cap - need) {
            b->probe_refused_arena += 1u;
            return -7;
        }
        if (!delta->payload) {
            return -8;
        }
        dst = b->arena + b->arena_used;
        memcpy(dst, delta->payload, (size_t)need);
        b->arena_used += need;
    } else {
        dst = (unsigned char *)0;
    }

    r = &b->records[b->count];
    memset(r, 0, sizeof(*r));
    r->key = *key;
    r->hdr = delta->hdr;
    r->payload = dst;
    r->payload_len = need;
    r->insert_index = b->count;
    b->count += 1u;
    return 0;
}

u32 dg_delta_buffer_count(const dg_delta_buffer *b) {
    return b ? b->count : 0u;
}

const dg_delta_record *dg_delta_buffer_at(const dg_delta_buffer *b, u32 index) {
    if (!b || !b->records || index >= b->count) {
        return (const dg_delta_record *)0;
    }
    return &b->records[index];
}

u32 dg_delta_buffer_probe_refused_records(const dg_delta_buffer *b) {
    return b ? b->probe_refused_records : 0u;
}

u32 dg_delta_buffer_probe_refused_arena(const dg_delta_buffer *b) {
    return b ? b->probe_refused_arena : 0u;
}

