/*
FILE: source/domino/sim/pkt/pkt_hash.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/pkt_hash
RESPONSIBILITY: Defines internal contract for `pkt_hash`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic packet hashing (C89).
 *
 * Hashes header fields + canonicalized TLV payload bytes using a stable
 * non-crypto 64-bit hash (FNV-1a).
 *
 * IMPORTANT: Header numeric fields are hashed using explicit little-endian
 * encoding, never by hashing raw struct bytes (padding/endianness).
 */
#ifndef DG_PKT_HASH_H
#define DG_PKT_HASH_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dg_pkt_hash;

/* Content-defined 64-bit ID helper (FNV-1a over bytes of NUL-terminated string). */
u64 dg_hash64_fnv1a_cstr(const char *s);

/* Compute deterministic packet hash. Returns 0 on success. */
int dg_pkt_hash_compute(
    dg_pkt_hash        *out_hash,
    const dg_pkt_hdr   *hdr,
    const unsigned char *payload,
    u32                 payload_len
);

/* Compute hash when payload is already canonical TLV order. Returns 0 on success. */
int dg_pkt_hash_compute_canon(
    dg_pkt_hash        *out_hash,
    const dg_pkt_hdr   *hdr,
    const unsigned char *canon_payload,
    u32                 payload_len
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_HASH_H */

