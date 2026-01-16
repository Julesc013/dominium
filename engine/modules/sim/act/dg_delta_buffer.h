/*
FILE: source/domino/sim/act/dg_delta_buffer.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/act/dg_delta_buffer
RESPONSIBILITY: Defines internal contract for `dg_delta_buffer`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Delta buffer (deterministic; C89).
 *
 * Buffers dg_pkt_delta packets for a single tick prior to commit.
 * Storage is bounded: max deltas and arena bytes are fixed by reserve().
 */
#ifndef DG_DELTA_BUFFER_H
#define DG_DELTA_BUFFER_H

#include "core/dg_order_key.h"
#include "sim/pkt/dg_pkt_delta.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_delta_record {
    dg_order_key        key;
    dg_pkt_hdr          hdr;         /* copied */
    const unsigned char *payload;    /* points into arena (or NULL) */
    u32                 payload_len;
    u32                 insert_index; /* stable tie-break/debug */
} dg_delta_record;

typedef struct dg_delta_buffer {
    dg_tick tick;

    dg_delta_record *records;
    u32              count;
    u32              capacity;

    unsigned char   *arena;
    u32              arena_cap;
    u32              arena_used;

    d_bool           owns_storage;

    u32 probe_refused_records;
    u32 probe_refused_arena;
} dg_delta_buffer;

void dg_delta_buffer_init(dg_delta_buffer *b);
void dg_delta_buffer_free(dg_delta_buffer *b);

/* Allocate bounded storage for the tick buffer. */
int dg_delta_buffer_reserve(dg_delta_buffer *b, u32 max_deltas, u32 arena_bytes);

void dg_delta_buffer_begin_tick(dg_delta_buffer *b, dg_tick tick);

/* Push a delta packet + canonical commit key.
 * Returns 0 on success; non-zero if refused (capacity/arena) or invalid.
 */
int dg_delta_buffer_push(dg_delta_buffer *b, const dg_order_key *key, const dg_pkt_delta *delta);

u32 dg_delta_buffer_count(const dg_delta_buffer *b);
const dg_delta_record *dg_delta_buffer_at(const dg_delta_buffer *b, u32 index);

u32 dg_delta_buffer_probe_refused_records(const dg_delta_buffer *b);
u32 dg_delta_buffer_probe_refused_arena(const dg_delta_buffer *b);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DELTA_BUFFER_H */

