/*
FILE: include/domino/core/d_tlv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/d_tlv
RESPONSIBILITY: Defines the public contract for `d_tlv` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Minimal TLV blob wrapper (public header).
 *
 * Canonical semantics live in `docs/specs/SPEC_CORE.md#Types and ids`.
 */
#ifndef D_TLV_H
#define D_TLV_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Non-owning view of an opaque binary payload (commonly TLV-encoded).
 *
 * Members:
 * - `ptr`: Pointer to the first byte of the payload. May be NULL when `len == 0`.
 * - `len`: Payload size in bytes.
 *
 * Ownership:
 * - `ptr` is borrowed; the owner controls allocation and lifetime.
 *
 * Determinism:
 * - The bytes are treated as opaque by this type; determinism depends on the producer/consumer.
 */
typedef struct d_tlv_blob {
    unsigned char *ptr;
    u32            len;
} d_tlv_blob;

#ifdef __cplusplus
}
#endif

#endif /* D_TLV_H */
