#include <string.h>
#include "core_internal.h"
#include "dominium/game_api.h"

#define DOM_SIM_STRUCT_VERSION 1u
#define DOM_SIM_DEFAULT_UPS 60.0

static dom_instance_record* dom_sim_find_instance(dom_core* core, dom_instance_id id)
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

static dom_sim_instance_state* dom_sim_find_state(dom_core* core, dom_instance_id id)
{
    uint32_t i;

    if (!core) {
        return NULL;
    }

    for (i = 0u; i < core->sim_state_count; ++i) {
        if (core->sim_states[i].id == id) {
            return &core->sim_states[i];
        }
    }

    return NULL;
}

static dom_sim_instance_state* dom_sim_get_or_create_state(dom_core* core, dom_instance_id id)
{
    dom_sim_instance_state* state;

    if (!core) {
        return NULL;
    }

    state = dom_sim_find_state(core, id);
    if (state) {
        return state;
    }

    if (core->sim_state_count >= DOM_MAX_SIM_STATES) {
        return NULL;
    }

    state = &core->sim_states[core->sim_state_count];
    memset(state, 0, sizeof(*state));
    state->id = id;
    state->ups = DOM_SIM_DEFAULT_UPS;
    state->dt_s = 1.0 / state->ups;
    state->paused = false;
    core->sim_state_count += 1u;
    return state;
}

bool dom_sim_tick(dom_core* core, dom_instance_id inst, uint32_t ticks)
{
    dom_instance_record*     inst_rec;
    dom_sim_instance_state*  sim_state;
    dom_event                ev;
    dom_game_sim_step_args   args;
    uint32_t                 i;
    uint32_t                 advanced;

    inst_rec = dom_sim_find_instance(core, inst);
    if (!inst_rec) {
        return false;
    }

    sim_state = dom_sim_get_or_create_state(core, inst);
    if (!sim_state) {
        return false;
    }

    if (sim_state->paused || ticks == 0u) {
        return true;
    }

    args.struct_size = sizeof(args);
    args.struct_version = 1;
    args.inst = inst;
    args.dt_s = sim_state->dt_s;

    advanced = 0u;
    for (i = 0u; i < ticks; ++i) {
        dom_game_sim_step(core, &args);
        sim_state->ticks += 1u;
        sim_state->sim_time_s += sim_state->dt_s;
        advanced += 1u;
    }

    if (advanced > 0u) {
        if (core) {
            core->tick_counter += advanced;
        }
        ev.struct_size = sizeof(dom_event);
        ev.struct_version = 1;
        ev.kind = DOM_EVT_SIM_TICKED;
        ev.u.inst_id = inst;
        dom_event__publish(core, &ev);
    }

    return true;
}

bool dom_sim_get_state(dom_core* core, dom_instance_id inst, dom_sim_state* out)
{
    dom_sim_instance_state* sim_state;
    dom_sim_state           zero;

    if (!out) {
        return false;
    }

    memset(&zero, 0, sizeof(zero));
    zero.struct_size = sizeof(dom_sim_state);
    zero.struct_version = DOM_SIM_STRUCT_VERSION;

    if (!core) {
        *out = zero;
        return false;
    }

    if (!dom_sim_find_instance(core, inst)) {
        *out = zero;
        return false;
    }

    sim_state = dom_sim_find_state(core, inst);
    if (!sim_state) {
        *out = zero;
        return true;
    }

    out->struct_size = sizeof(dom_sim_state);
    out->struct_version = DOM_SIM_STRUCT_VERSION;
    out->ticks = sim_state->ticks;
    out->sim_time_s = sim_state->sim_time_s;
    out->dt_s = sim_state->dt_s;
    out->ups = sim_state->ups;
    out->paused = sim_state->paused;
    return true;
}
