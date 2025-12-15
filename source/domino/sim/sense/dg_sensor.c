#include "sim/sense/dg_sensor.h"

d_bool dg_sensor_should_run(const dg_sensor_desc *s, dg_tick tick, dg_agent_id agent_id) {
    u64 stable_id;
    if (!s) {
        return D_FALSE;
    }
    /* Combine keys; dg_stride_should_run hashes stable_id internally. */
    stable_id = ((u64)agent_id) ^ (s->sensor_id * 11400714819323198485ULL);
    return dg_stride_should_run(tick, stable_id, s->stride);
}

u32 dg_sensor_estimate_cost(const dg_sensor_desc *s, dg_agent_id agent_id, const void *observer_ctx, u32 default_cost) {
    if (!s) {
        return default_cost;
    }
    if (s->vtbl.estimate_cost) {
        return s->vtbl.estimate_cost(agent_id, observer_ctx);
    }
    return default_cost;
}

