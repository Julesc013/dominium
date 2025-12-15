#include "agent/group/dg_group_ctrl.h"

d_bool dg_group_ctrl_should_run(const dg_group_ctrl_desc *c, dg_tick tick, dg_group_id group_id) {
    u64 stable_id;
    if (!c) {
        return D_FALSE;
    }
    stable_id = ((u64)group_id) ^ (c->ctrl_id * 11400714819323198485ULL);
    return dg_stride_should_run(tick, stable_id, c->stride);
}

u32 dg_group_ctrl_estimate_cost(
    const dg_group_ctrl_desc    *c,
    dg_group_id                  group_id,
    const dg_group              *group,
    const dg_observation_buffer *observations,
    const void                  *internal_state,
    u32                          default_cost
) {
    if (!c) {
        return default_cost;
    }
    if (c->vtbl.estimate_cost) {
        return c->vtbl.estimate_cost(group_id, group, observations, internal_state);
    }
    return default_cost;
}

