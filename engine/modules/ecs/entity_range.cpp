/*
FILE: engine/modules/ecs/entity_range.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: EntityRange helpers.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable range evaluation only.
*/
#include "domino/ecs/ecs_entity_range.h"

u32 dom_entity_range_count(const dom_entity_range* range)
{
    if (!range) {
        return 0u;
    }
    if (range->end_index < range->begin_index) {
        return 0u;
    }
    return range->end_index - range->begin_index;
}

d_bool dom_entity_range_is_valid(const dom_entity_range* range)
{
    if (!range) {
        return D_FALSE;
    }
    if (!dom_archetype_id_is_valid(range->archetype_id)) {
        return D_FALSE;
    }
    if (range->end_index < range->begin_index) {
        return D_FALSE;
    }
    return D_TRUE;
}

d_bool dom_entity_range_contains(const dom_entity_range* range, u32 index)
{
    if (!dom_entity_range_is_valid(range)) {
        return D_FALSE;
    }
    return (index >= range->begin_index && index < range->end_index) ? D_TRUE : D_FALSE;
}
