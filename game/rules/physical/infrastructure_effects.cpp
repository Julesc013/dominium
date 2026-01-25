/*
FILE: game/rules/physical/infrastructure_effects.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Applies infrastructure availability to agent capability masks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Capability propagation is deterministic for identical inputs.
*/
#include "dominium/physical/infrastructure_effects.h"

static dom_agent_capability* dom_infra_find_cap(dom_agent_capability* caps,
                                                u32 cap_count,
                                                u64 agent_id)
{
    u32 i;
    if (!caps) {
        return 0;
    }
    for (i = 0u; i < cap_count; ++i) {
        if (caps[i].agent_id == agent_id) {
            return &caps[i];
        }
    }
    return 0;
}

void dom_infra_apply_agent_caps(dom_agent_capability* caps,
                                u32 cap_count,
                                const dom_network_graph* network,
                                const dom_infra_binding* bindings,
                                u32 binding_count)
{
    u32 i;
    if (!caps || !bindings || binding_count == 0u) {
        return;
    }
    for (i = 0u; i < binding_count; ++i) {
        const dom_infra_binding* binding = &bindings[i];
        dom_agent_capability* cap = dom_infra_find_cap(caps, cap_count, binding->agent_id);
        if (!cap) {
            continue;
        }
        if (network) {
            dom_network_node* node = dom_network_find_node((dom_network_graph*)network, binding->node_id);
            if (node && node->status == DOM_NETWORK_OK) {
                cap->capability_mask |= binding->capability_mask;
            } else {
                cap->capability_mask &= ~binding->capability_mask;
            }
        } else {
            cap->capability_mask &= ~binding->capability_mask;
        }
    }
}
