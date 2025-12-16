/*
FILE: source/domino/decor/compile/dg_decor_dirty.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_dirty
RESPONSIBILITY: Implements `dg_decor_dirty`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR incremental dirty tracking (C89). */
#ifndef DG_DECOR_DIRTY_H
#define DG_DECOR_DIRTY_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"

#include "decor/model/dg_decor_host.h"
#include "decor/model/dg_decor_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_decor_dirty_rulepack {
    dg_decor_rulepack_id rulepack_id;
    d_bool               dirty;
} dg_decor_dirty_rulepack;

typedef struct dg_decor_dirty_host {
    dg_decor_host host; /* canonical key */
    dg_chunk_id   chunk_id;
    d_bool        dirty;
} dg_decor_dirty_host;

typedef struct dg_decor_dirty_chunk {
    dg_chunk_id chunk_id;
    d_bool      dirty;
} dg_decor_dirty_chunk;

typedef struct dg_decor_dirty {
    dg_decor_dirty_rulepack *rulepacks; /* sorted by rulepack_id */
    u32                      rulepack_count;
    u32                      rulepack_capacity;

    dg_decor_dirty_host *hosts; /* sorted by dg_decor_host_cmp */
    u32                  host_count;
    u32                  host_capacity;

    dg_decor_dirty_chunk *chunks; /* sorted by chunk_id */
    u32                   chunk_count;
    u32                   chunk_capacity;

    d_bool overrides_dirty;
    u32    _pad32;
} dg_decor_dirty;

void dg_decor_dirty_init(dg_decor_dirty *d);
void dg_decor_dirty_free(dg_decor_dirty *d);
void dg_decor_dirty_clear(dg_decor_dirty *d);

int dg_decor_dirty_reserve_rulepacks(dg_decor_dirty *d, u32 capacity);
int dg_decor_dirty_reserve_hosts(dg_decor_dirty *d, u32 capacity);
int dg_decor_dirty_reserve_chunks(dg_decor_dirty *d, u32 capacity);

void dg_decor_dirty_mark_overrides(dg_decor_dirty *d);
void dg_decor_dirty_mark_rulepack(dg_decor_dirty *d, dg_decor_rulepack_id rulepack_id);
void dg_decor_dirty_mark_host(dg_decor_dirty *d, const dg_decor_host *host, dg_chunk_id chunk_id);
void dg_decor_dirty_mark_chunk(dg_decor_dirty *d, dg_chunk_id chunk_id);

/* Query (returns 1 if found, 0 if not). */
int dg_decor_dirty_get_host(const dg_decor_dirty *d, const dg_decor_host *host, dg_decor_dirty_host *out);
int dg_decor_dirty_get_chunk(const dg_decor_dirty *d, dg_chunk_id chunk_id, dg_decor_dirty_chunk *out);

/* Clear dirty flag for a specific host/chunk/rulepack (no-op if absent). */
void dg_decor_dirty_clear_host(dg_decor_dirty *d, const dg_decor_host *host);
void dg_decor_dirty_clear_chunk(dg_decor_dirty *d, dg_chunk_id chunk_id);
void dg_decor_dirty_clear_rulepack(dg_decor_dirty *d, dg_decor_rulepack_id rulepack_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_DIRTY_H */

