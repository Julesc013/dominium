/*
FILE: include/dominium/physical/infrastructure_effects.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Applies infrastructure availability to agent capability masks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Capability propagation is deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_INFRASTRUCTURE_EFFECTS_H
#define DOMINIUM_PHYSICAL_INFRASTRUCTURE_EFFECTS_H

#include "dominium/physical/network_graph.h"
#include "dominium/rules/agents/agent_planning_tasks.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_infra_binding {
    u64 agent_id;
    u64 node_id;
    u32 capability_mask;
} dom_infra_binding;

void dom_infra_apply_agent_caps(dom_agent_capability* caps,
                                u32 cap_count,
                                const dom_network_graph* network,
                                const dom_infra_binding* bindings,
                                u32 binding_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_INFRASTRUCTURE_EFFECTS_H */
