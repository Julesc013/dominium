/*
FILE: source/domino/system/core/base/dom_core/dom_core_id.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_id
RESPONSIBILITY: Implements `dom_core_id`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_core_id.h"

#define DOM_ENTITY_INDEX_MASK ((dom_u64)0xFFFFFFFFu)
#define DOM_ENTITY_GEN_SHIFT  32

dom_entity_id dom_entity_make(dom_u32 index, dom_u32 generation)
{
    return ((dom_entity_id)generation << DOM_ENTITY_GEN_SHIFT) | (dom_entity_id)index;
}

dom_u32 dom_entity_index(dom_entity_id e)
{
    return (dom_u32)(e & DOM_ENTITY_INDEX_MASK);
}

dom_u32 dom_entity_generation(dom_entity_id e)
{
    return (dom_u32)(e >> DOM_ENTITY_GEN_SHIFT);
}
