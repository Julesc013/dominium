/*
FILE: include/domino/core/d_tlv_kv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / d_tlv_kv
RESPONSIBILITY: Public key/value TLV helpers shared across subsystems.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Simple key/value TLV helpers (C89).
 * Format: tag (u32) + length (u32) + payload bytes.
 * This is used in multiple places for nested parameter blobs.
 */
#ifndef D_TLV_KV_H
#define D_TLV_KV_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

int d_tlv_kv_next(const d_tlv_blob *blob,
                  u32 *offset,
                  u32 *tag,
                  d_tlv_blob *payload);
int d_tlv_kv_read_u32(const d_tlv_blob *payload, u32 *out);
int d_tlv_kv_read_u16(const d_tlv_blob *payload, u16 *out);
int d_tlv_kv_read_q16_16(const d_tlv_blob *payload, q16_16 *out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_TLV_KV_H */
