/*
FILE: source/domino/sim/_legacy/core_sim/dom_sim_ecs.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/dom_sim_ecs
RESPONSIBILITY: Defines internal contract for `dom_sim_ecs`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SIM_ECS_H
#define DOM_SIM_ECS_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"
#include "dom_sim_tick.h"

#define DOM_SIM_ECS_MAX_COMPONENTS 256
#define DOM_SIM_ECS_MAX_ENTITIES   65536

typedef dom_u16 DomComponentId;

typedef struct DomComponentInfo {
    DomComponentId id;
    const char    *name;
    dom_u32        size;
    dom_u32        align;
    dom_u32        flags;
} DomComponentInfo;

dom_err_t       dom_sim_ecs_init(void);
void            dom_sim_ecs_reset(void);

DomComponentId  dom_sim_ecs_register_component(const DomComponentInfo *info);
const DomComponentInfo *dom_sim_ecs_component_info(DomComponentId id);

dom_entity_id   dom_sim_ecs_create_entity(void);
dom_err_t       dom_sim_ecs_destroy_entity(dom_entity_id e);
dom_bool8       dom_sim_ecs_is_alive(dom_entity_id e);

dom_u32         dom_sim_ecs_active_count(void);
dom_entity_id   dom_sim_ecs_active_at(dom_u32 index);

dom_err_t dom_sim_ecs_add_component(dom_entity_id e, DomComponentId cid, const void *data);
dom_err_t dom_sim_ecs_remove_component(dom_entity_id e, DomComponentId cid);
void     *dom_sim_ecs_component_ptr(DomComponentId cid, dom_entity_id e);

dom_u32       dom_sim_ecs_component_count(DomComponentId cid);
dom_entity_id dom_sim_ecs_component_entity_at(DomComponentId cid, dom_u32 index);

DomLaneId dom_sim_ecs_lane_of(dom_entity_id e);

#endif /* DOM_SIM_ECS_H */
