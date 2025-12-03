#ifndef DOM_CORE_ID_H
#define DOM_CORE_ID_H

#include "dom_core_types.h"

/* Entity handle: 32-bit index + 32-bit generation */
typedef dom_u64 dom_entity_id;

dom_entity_id dom_entity_make(dom_u32 index, dom_u32 generation);
dom_u32       dom_entity_index(dom_entity_id e);
dom_u32       dom_entity_generation(dom_entity_id e);

/* World hierarchy IDs */
typedef dom_u32 dom_surface_id;
typedef dom_u32 dom_planet_id;
typedef dom_u32 dom_system_id;
typedef dom_u32 dom_galaxy_id;
typedef dom_u32 dom_universe_id;

#endif /* DOM_CORE_ID_H */
