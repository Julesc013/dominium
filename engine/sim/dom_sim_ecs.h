#ifndef DOM_SIM_ECS_H
#define DOM_SIM_ECS_H

#include "dom_core_types.h"
#include "dom_core_id.h"
#include "dom_core_err.h"

#define DOM_ECS_MAX_COMPONENTS 256
#define DOM_ECS_MAX_ENTITIES   65536

typedef dom_u16 DomComponentId;

typedef struct DomComponentInfo {
    DomComponentId id;
    const char    *name;
    dom_u32        size;
    dom_u32        align;
    dom_u32        flags;
} DomComponentInfo;

dom_err_t       dom_sim_ecs_init(void);
DomComponentId  dom_sim_ecs_register_component(const DomComponentInfo *info);
dom_entity_id   dom_sim_ecs_create_entity(void);
void            dom_sim_ecs_destroy_entity(dom_entity_id e);
dom_bool8       dom_sim_ecs_is_alive(dom_entity_id e);
dom_u32         dom_sim_ecs_active_count(void);
dom_entity_id   dom_sim_ecs_active_at(dom_u32 index);

#endif /* DOM_SIM_ECS_H */
