/* Typed packet ABI (deterministic; C89).
 *
 * Packet structs are POD views over (header + external TLV payload bytes).
 * Packet payload bytes are NOT stored inline and MUST NOT be treated as a
 * serialized struct blob (no padding, no pointers).
 *
 * Numeric fields in deterministic IO MUST be encoded explicitly as little-endian
 * when serialized/hashes are computed; do not hash/serialize raw struct bytes.
 */
#ifndef DG_PKT_COMMON_H
#define DG_PKT_COMMON_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* 64-bit IDs for typed packet taxonomy and schema ids. */
typedef u64 dg_type_id;
typedef u64 dg_schema_id;

/* Simulation tick counter. Chosen as 64-bit to avoid rollover in long runs. */
typedef u64 dg_tick;

/* Stable numeric identifiers referenced by packets. */
typedef u64 dg_entity_id;
typedef u64 dg_domain_id;
typedef u64 dg_chunk_id;

/* Packet header flags (extend as needed; must remain deterministic). */
#define DG_PKT_FLAG_NONE 0u

/* Canonical little-endian wire size of dg_pkt_hdr (no padding). */
#define DG_PKT_HDR_WIRE_BYTES 68u

/* Common deterministic packet header.
 * NOTE: Do not serialize/hash this struct directly; use explicit LE encoding.
 */
typedef struct dg_pkt_hdr {
    dg_type_id   type_id;      /* packet type (taxonomy) */
    dg_schema_id schema_id;    /* schema identifier for payload */
    u16          schema_ver;   /* schema version for payload */
    u16          flags;        /* DG_PKT_FLAG_* */
    dg_tick      tick;         /* authoritative tick */
    dg_entity_id src_entity;   /* optional; 0 means none */
    dg_entity_id dst_entity;   /* optional; 0 means none/broadcast */
    dg_domain_id domain_id;    /* stable domain id (0 allowed) */
    dg_chunk_id  chunk_id;     /* stable chunk id (0 allowed) */
    u32          seq;          /* stable ordering within tick/phase */
    u32          payload_len;  /* payload byte length (TLV container) */
} dg_pkt_hdr;

void dg_pkt_hdr_clear(dg_pkt_hdr *hdr);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_COMMON_H */

