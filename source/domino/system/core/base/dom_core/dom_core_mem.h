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
