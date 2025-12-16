/*
FILE: source/domino/sim/hash/dg_hash_stream.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/hash/dg_hash_stream
RESPONSIBILITY: Implements `dg_hash_stream`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Canonical hash stream (C89).
 *
 * Hash streams consume canonicalized bytes and explicit-LE encoded integers.
 * Callers MUST NOT hash raw struct memory or pointer values.
 */
#ifndef DG_HASH_STREAM_H
#define DG_HASH_STREAM_H

#include "domino/core/types.h"
#include "sim/pkt/dg_pkt_common.h"

#include "sim/hash/dg_hash.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_hash_stream {
    dg_hash_value h;
} dg_hash_stream;

void dg_hash_stream_init(dg_hash_stream *s);

/* Reset to a canonical per-domain/tick seed and include (domain_id,tick). */
void dg_hash_stream_begin_domain(dg_hash_stream *s, dg_hash_domain_id domain_id, dg_tick tick);

void dg_hash_stream_update_bytes(dg_hash_stream *s, const unsigned char *data, u32 len);

void dg_hash_stream_update_u16_le(dg_hash_stream *s, u16 v);
void dg_hash_stream_update_u32_le(dg_hash_stream *s, u32 v);
void dg_hash_stream_update_u64_le(dg_hash_stream *s, u64 v);
void dg_hash_stream_update_i64_le(dg_hash_stream *s, i64 v);

dg_hash_value dg_hash_stream_finalize(const dg_hash_stream *s);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_HASH_STREAM_H */

