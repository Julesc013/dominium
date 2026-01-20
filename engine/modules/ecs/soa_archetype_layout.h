/*
FILE: engine/modules/ecs/soa_archetype_layout.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: SoA archetype layout helpers (component set + field defs).
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable ordering and stable ID derivation only.
*/
#ifndef DOMINO_ECS_SOA_ARCHETYPE_LAYOUT_H
#define DOMINO_ECS_SOA_ARCHETYPE_LAYOUT_H

#include "domino/ecs/ecs_archetype_id.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_soa_field_def {
    dom_field_id field_id;
    u32          element_type;
    u32          element_size;
} dom_soa_field_def;

typedef struct dom_soa_component_def {
    dom_component_id      component_id;
    const dom_soa_field_def* fields;
    u32                   field_count;
} dom_soa_component_def;

void dom_soa_sort_component_ids(dom_component_id* ids, u32 count);
void dom_soa_sort_field_defs(dom_soa_field_def* fields, u32 count);
d_bool dom_soa_component_set_is_sorted(const dom_component_id* ids, u32 count);
dom_archetype_id dom_soa_archetype_id_from_components(const dom_component_id* ids, u32 count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_SOA_ARCHETYPE_LAYOUT_H */
