/*
FILE: source/domino/ecs/ecs_archetype_id.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ecs/archetype_id
RESPONSIBILITY: Implements ECS archetype identifier helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Stable identifiers only; no pointer-based IDs.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/ecs/ecs_archetype_id.h"

dom_archetype_id dom_archetype_id_make(u64 value)
{
    dom_archetype_id id;
    dom_archetype_id *ptr = &id;
    ptr->value = value;
    return id;
}

d_bool dom_archetype_id_equal(dom_archetype_id a, dom_archetype_id b)
{
    const dom_archetype_id *pa = &a;
    const dom_archetype_id *pb = &b;
    return (pa->value == pb->value) ? D_TRUE : D_FALSE;
}

d_bool dom_archetype_id_is_valid(dom_archetype_id id)
{
    const dom_archetype_id *ptr = &id;
    return (ptr->value != 0u) ? D_TRUE : D_FALSE;
}
