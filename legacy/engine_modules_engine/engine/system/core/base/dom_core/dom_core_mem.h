/*
FILE: source/domino/system/core/base/dom_core/dom_core_mem.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_mem
RESPONSIBILITY: Defines internal contract for `dom_core_mem`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CORE_MEM_H
#define DOM_CORE_MEM_H

#include "dom_core_types.h"
#include "dom_core_err.h"

/* Basic allocation wrappers */
void *dom_alloc(dom_u32 size);
void  dom_free(void *ptr);
void *dom_realloc(void *ptr, dom_u32 new_size);
void *dom_alloc_zero(dom_u32 size);

/* Linear arena (caller supplies backing buffer) */
typedef struct DomArena {
    dom_u8  *base;
    dom_u32  capacity;
    dom_u32  used;
} DomArena;

dom_err_t dom_arena_init(DomArena *arena, void *buffer, dom_u32 size);
void     *dom_arena_alloc(DomArena *arena, dom_u32 size);
void     *dom_arena_alloc_zero(DomArena *arena, dom_u32 size);
void      dom_arena_reset(DomArena *arena);

dom_u32 dom_align_up(dom_u32 value, dom_u32 align);
dom_u32 dom_align_down(dom_u32 value, dom_u32 align);

#endif /* DOM_CORE_MEM_H */
