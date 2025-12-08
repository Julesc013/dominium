#include <string.h>
#include "core_internal.h"

static dom_instance_record* dom_sim_find(dom_core* core, dom_instance_id id)
{
    uint32_t i;

    if (!core) {
        return NULL;
    }

    for (i = 0; i < core->instance_count; ++i) {
        if (core->instances[i].info.id == id) {
            return &core->instances[i];
        }
    }

    return NULL;
}

bool dom_sim_tick(dom_core* core, dom_instance_id inst, uint32_t ticks)
{
    dom_instance_record* rec;
    double dt;

    rec = dom_sim_find(core, inst);
    if (!rec) {
        return false;
    }

    dt = ((double)ticks) / 60.0;
    rec->sim.ticks += ticks;
    rec->sim.dt_s = dt;
    rec->sim.sim_time_s += dt;

    if (core) {
        core->tick_counter += ticks;
    }

    return true;
}

bool dom_sim_get_state(dom_core* core, dom_instance_id inst, dom_sim_state* out)
{
    dom_instance_record* rec;

    if (!out) {
        return false;
    }

    rec = dom_sim_find(core, inst);
    if (!rec) {
        return false;
    }

    rec->sim.struct_size = sizeof(dom_sim_state);
    rec->sim.struct_version = 1;
    *out = rec->sim;
    return true;
}
