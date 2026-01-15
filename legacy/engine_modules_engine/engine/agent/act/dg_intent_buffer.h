/*
FILE: source/domino/agent/act/dg_intent_buffer.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/act/dg_intent_buffer
RESPONSIBILITY: Defines internal contract for `dg_intent_buffer`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Intent buffer (deterministic; C89).
 *
 * Buffers dg_pkt_intent packets for a single tick prior to action dispatch.
 * Storage is bounded: max intents and arena bytes are fixed by reserve().
 *
 * Canonical ordering (authoritative):
 *   (tick, agent_id, intent_type_id, seq)
 * where agent_id is hdr.src_entity and intent_type_id is hdr.type_id.
 */
#ifndef DG_INTENT_BUFFER_H
#define DG_INTENT_BUFFER_H

#include "agent/dg_agent_ids.h"
#include "sim/pkt/dg_pkt_intent.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_intent_record {
    dg_pkt_hdr          hdr;      /* copied */
    const unsigned char *payload; /* points into arena (or NULL) */
    u32                 payload_len;
} dg_intent_record;

typedef struct dg_intent_buffer {
    dg_tick tick;

    dg_intent_record *records;
    u32               count;
    u32               capacity;

    unsigned char *arena;
    u32            arena_cap;
    u32            arena_used;

    d_bool owns_storage;

    u32 probe_refused_records;
    u32 probe_refused_arena;
} dg_intent_buffer;

void dg_intent_buffer_init(dg_intent_buffer *b);
void dg_intent_buffer_free(dg_intent_buffer *b);

/* Allocate bounded storage for the tick buffer. */
int dg_intent_buffer_reserve(dg_intent_buffer *b, u32 max_intents, u32 arena_bytes);

void dg_intent_buffer_begin_tick(dg_intent_buffer *b, dg_tick tick);

/* Push an intent packet. Returns 0 on success; non-zero if refused/invalid. */
int dg_intent_buffer_push(dg_intent_buffer *b, const dg_pkt_intent *intent);

/* Sort records into canonical deterministic order for stable iteration/comparison. */
void dg_intent_buffer_canonize(dg_intent_buffer *b);

u32 dg_intent_buffer_count(const dg_intent_buffer *b);
const dg_intent_record *dg_intent_buffer_at(const dg_intent_buffer *b, u32 index);

u32 dg_intent_buffer_probe_refused_records(const dg_intent_buffer *b);
u32 dg_intent_buffer_probe_refused_arena(const dg_intent_buffer *b);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_INTENT_BUFFER_H */

