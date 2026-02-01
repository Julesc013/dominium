/*
FILE: source/domino/core/d_tlv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_tlv
RESPONSIBILITY: Defines internal contract for `d_tlv`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Minimal TLV blob wrapper. */
#ifndef D_TLV_H
#define D_TLV_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_tlv_blob {
    unsigned char *ptr;
    u32            len;
} d_tlv_blob;

#ifdef __cplusplus
}
#endif

#endif /* D_TLV_H */
