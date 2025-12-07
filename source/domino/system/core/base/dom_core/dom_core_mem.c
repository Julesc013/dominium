#include "dom_core_mem.h"
#include <stdlib.h>
#include <string.h>

void *dom_alloc(dom_u32 size)
{
    if (size == 0) return 0;
    return malloc(size);
}

void dom_free(void *ptr)
{
    if (ptr) free(ptr);
}

void *dom_realloc(void *ptr, dom_u32 new_size)
{
    return realloc(ptr, new_size);
}

void *dom_alloc_zero(dom_u32 size)
{
    void *p = dom_alloc(size);
    if (p) memset(p, 0, size);
    return p;
}

dom_err_t dom_arena_init(DomArena *arena, void *buffer, dom_u32 size)
{
    if (!arena || !buffer || size == 0) return DOM_ERR_INVALID_ARG;
    arena->base = (dom_u8 *)buffer;
    arena->capacity = size;
    arena->used = 0;
    return DOM_OK;
}

void *dom_arena_alloc(DomArena *arena, dom_u32 size)
{
    dom_u32 next = arena->used + size;
    if (next > arena->capacity) return 0;
    {
        void *ptr = arena->base + arena->used;
        arena->used = next;
        return ptr;
    }
}

void *dom_arena_alloc_zero(DomArena *arena, dom_u32 size)
{
    void *ptr = dom_arena_alloc(arena, size);
    if (ptr) memset(ptr, 0, size);
    return ptr;
}

void dom_arena_reset(DomArena *arena)
{
    if (arena) arena->used = 0;
}

dom_u32 dom_align_up(dom_u32 value, dom_u32 align)
{
    if (align == 0) return value;
    {
        dom_u32 rem = value % align;
        return rem ? (value + (align - rem)) : value;
    }
}

dom_u32 dom_align_down(dom_u32 value, dom_u32 align)
{
    if (align == 0) return value;
    return value - (value % align);
}
