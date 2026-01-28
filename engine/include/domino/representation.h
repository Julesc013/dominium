/*
FILE: include/domino/representation.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / representation
RESPONSIBILITY: Defines representation tier metadata (explicit/hybrid/procedural).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Metadata only; MUST NOT alter simulation logic.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/architectureitecture/**`.
*/
#ifndef DOMINO_REPRESENTATION_H
#define DOMINO_REPRESENTATION_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_representation_tier: Declarative representation tier (no behavior). */
typedef enum dom_representation_tier {
    DOM_REPRESENTATION_EXPLICIT = 0,
    DOM_REPRESENTATION_HYBRID = 1,
    DOM_REPRESENTATION_PROCEDURAL = 2
} dom_representation_tier;

/* dom_representation_meta: Optional metadata bundle for tier + LOD context. */
typedef struct dom_representation_meta {
    dom_representation_tier tier;
    u32                     lod_index;
    u32                     flags;
} dom_representation_meta;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_REPRESENTATION_H */
