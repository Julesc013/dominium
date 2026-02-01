/*
FILE: source/domino/res/dg_tlv_canon.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/dg_tlv_canon
RESPONSIBILITY: Defines internal contract for `dg_tlv_canon`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Canonical TLV utilities (deterministic; C89).
 *
 * Format: [tag:u32_le][len:u32_le][payload bytes]...
 *
 * Canonicalization is structural: records are sorted by (tag, payload bytes).
 * No gameplay semantics are applied here. Numeric parsing is explicit LE.
 */
#ifndef DG_TLV_CANON_H
#define DG_TLV_CANON_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Explicit little-endian helpers (no host-endian memcpy). */
u16 dg_le_read_u16(const unsigned char *p);
u32 dg_le_read_u32(const unsigned char *p);
u64 dg_le_read_u64(const unsigned char *p);
void dg_le_write_u16(unsigned char *p, u16 v);
void dg_le_write_u32(unsigned char *p, u32 v);
void dg_le_write_u64(unsigned char *p, u64 v);

/* Iterate TLV records. Returns:
 *  0: success, outputs filled, *offset advanced
 *  1: end-of-container reached
 * <0: malformed input
 */
int dg_tlv_next(
    const unsigned char  *tlv,
    u32                   tlv_len,
    u32                  *offset,
    u32                  *tag_out,
    const unsigned char **payload_out,
    u32                  *payload_len_out
);

/* Canonicalize a TLV container into 'out' by sorting records by (tag,payload).
 * out_cap must be >= tlv_len for a successful canonicalization.
 * Returns 0 on success, non-zero on error.
 */
int dg_tlv_canon(
    const unsigned char *tlv,
    u32                  tlv_len,
    unsigned char       *out,
    u32                  out_cap,
    u32                 *out_len
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TLV_CANON_H */

