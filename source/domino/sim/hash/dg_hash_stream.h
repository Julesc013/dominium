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

