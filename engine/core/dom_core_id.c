#include "dom_core_id.h"

#define DOM_ENTITY_INDEX_MASK 0xFFFFFFFFULL
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
