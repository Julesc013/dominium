/*
FILE: source/domino/core/d_tlv_kv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_tlv_kv
RESPONSIBILITY: Defines internal contract for `d_tlv_kv`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Simple key/value TLV helpers (C89).
 * Format: tag (u32) + length (u32) + payload bytes.
 * This is used in multiple places for nested parameter blobs.
 */
#ifndef DOMINO_CORE_D_TLV_KV_INTERNAL_H
#define DOMINO_CORE_D_TLV_KV_INTERNAL_H

#include "domino/core/d_tlv_kv.h"

#endif /* DOMINO_CORE_D_TLV_KV_INTERNAL_H */
