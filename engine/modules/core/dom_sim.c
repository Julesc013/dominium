/*
FILE: source/domino/core/dom_sim.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dom_sim
RESPONSIBILITY: Implements `dom_sim` core-facing API stubs (tick/state).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: State transitions are deterministic given identical inputs.
VERSIONING / ABI / DATA FORMAT NOTES: Uses public `dom_sim_state` layout.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "core_internal.h"

#define DOM_SIM_DEFAULT_UPS 60u

static dom_sim_instance_state* dom_sim_find_state(dom_core* core, dom_instance_id id)
{
    u32 i;
    if (!core || id == 0u) {
        return (dom_sim_instance_state*)0;
    }
    for (i = 0u; i < core->sim_state_count; ++i) {
        if (core->sim_states[i].id == id) {
            return &core->sim_states[i];
        }
    }
    return (dom_sim_instance_state*)0;
}

static void dom_sim_state_init(dom_sim_instance_state* state, dom_instance_id id)
{
    if (!state) {
        return;
    }
    state->id = id;
    state->ticks = 0u;
    state->sim_time_usec = 0u;
    state->ups = DOM_SIM_DEFAULT_UPS;
    state->dt_usec = (state->ups > 0u) ? (1000000u / state->ups) : 0u;
    state->paused = false;
}

static dom_sim_instance_state* dom_sim_get_or_create_state(dom_core* core, dom_instance_id id)
{
    dom_sim_instance_state* state;
    dom_instance_info info;

    state = dom_sim_find_state(core, id);
    if (state) {
        return state;
    }

    if (!dom_inst_get(core, id, &info)) {
        return (dom_sim_instance_state*)0;
    }
    if (core->sim_state_count >= DOM_MAX_SIM_STATES) {
        return (dom_sim_instance_state*)0;
    }

    state = &core->sim_states[core->sim_state_count++];
    dom_sim_state_init(state, id);
    return state;
}

bool dom_sim_tick(dom_core* core, dom_instance_id inst, uint32_t ticks)
{
    dom_sim_instance_state* state;
    if (!core || inst == 0u) {
        return false;
    }
    if (ticks == 0u) {
        return true;
    }
    state = dom_sim_get_or_create_state(core, inst);
    if (!state) {
        return false;
    }
    if (!state->paused) {
        state->ticks += (u64)ticks;
        state->sim_time_usec += (u64)state->dt_usec * (u64)ticks;
        core->tick_counter += (u64)ticks;
    }
    return true;
}

bool dom_sim_get_state(dom_core* core, dom_instance_id inst, dom_sim_state* out)
{
    dom_sim_instance_state* state;
    if (!core || !out || inst == 0u) {
        return false;
    }
    state = dom_sim_get_or_create_state(core, inst);
    if (!state) {
        return false;
    }
    out->struct_size = (u32)sizeof(dom_sim_state);
    out->struct_version = 2u;
    out->ticks = state->ticks;
    out->sim_time_usec = state->sim_time_usec;
    out->dt_usec = state->dt_usec;
    out->ups = state->ups;
    out->paused = state->paused;
    return true;
}
