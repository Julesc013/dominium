/*
FILE: include/domino/core/d_tlv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/d_tlv
RESPONSIBILITY: Defines the public contract for `d_tlv` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Minimal TLV blob wrapper (public header). */
#ifndef D_TLV_H
#define D_TLV_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_tlv_blob: Public type used by `d_tlv`. */
typedef struct d_tlv_blob {
    unsigned char *ptr;
    u32            len;
} d_tlv_blob;

#ifdef __cplusplus
}
#endif

#endif /* D_TLV_H */
