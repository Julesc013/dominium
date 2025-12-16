/*
FILE: source/domino/core/d_tlv_kv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_tlv_kv
RESPONSIBILITY: Defines internal contract for `d_tlv_kv`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Simple key/value TLV helpers (C89).
 * Format: tag (u32) + length (u32) + payload bytes.
 * This is used in multiple places for nested parameter blobs.
 */
#ifndef D_TLV_KV_H
#define D_TLV_KV_H

#include <string.h>

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"

static int d_tlv_kv_next(
    const d_tlv_blob *blob,
    u32              *offset,
    u32              *tag,
    d_tlv_blob       *payload
) {
    u32 remaining;
    u32 len;
    if (!blob || !offset || !tag || !payload) {
        return -1;
    }
    if (*offset >= blob->len) {
        return 1;
    }
    remaining = blob->len - *offset;
    if (remaining < 8u || !blob->ptr) {
        return -1;
    }
    memcpy(tag, blob->ptr + *offset, sizeof(u32));
    memcpy(&len, blob->ptr + *offset + 4u, sizeof(u32));
    *offset += 8u;
    if (len > blob->len - *offset) {
        return -1;
    }
    payload->ptr = blob->ptr + *offset;
    payload->len = len;
    *offset += len;
    return 0;
}

static int d_tlv_kv_read_u32(const d_tlv_blob *payload, u32 *out) {
    if (!payload || !out || !payload->ptr) {
        return -1;
    }
    if (payload->len != 4u) {
        return -1;
    }
    memcpy(out, payload->ptr, sizeof(u32));
    return 0;
}

static int d_tlv_kv_read_u16(const d_tlv_blob *payload, u16 *out) {
    if (!payload || !out || !payload->ptr) {
        return -1;
    }
    if (payload->len == 2u) {
        memcpy(out, payload->ptr, sizeof(u16));
        return 0;
    }
    if (payload->len == 4u) {
        u32 tmp;
        memcpy(&tmp, payload->ptr, sizeof(u32));
        *out = (u16)tmp;
        return 0;
    }
    return -1;
}

static int d_tlv_kv_read_q16_16(const d_tlv_blob *payload, q16_16 *out) {
    i32 tmp;
    if (!payload || !out || !payload->ptr) {
        return -1;
    }
    if (payload->len != 4u) {
        return -1;
    }
    memcpy(&tmp, payload->ptr, sizeof(i32));
    *out = (q16_16)tmp;
    return 0;
}

#endif /* D_TLV_KV_H */

