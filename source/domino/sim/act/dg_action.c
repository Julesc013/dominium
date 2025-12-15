#include "sim/act/dg_action.h"

u32 dg_action_estimate_cost(
    const dg_action_vtbl *vtbl,
    dg_agent_id           agent_id,
    const dg_pkt_intent  *intent,
    const void           *world_state,
    u32                   default_cost
) {
    if (!vtbl) {
        return default_cost;
    }
    if (vtbl->estimate_cost) {
        return vtbl->estimate_cost(agent_id, intent, world_state);
    }
    return default_cost;
}

