#include "dominium/actors.h"

typedef struct dom_actors_sim_state {
    dom_instance_id inst;
    uint64_t        step_count;
} dom_actors_sim_state;

#define DOM_ACTORS_MAX_SIM_STATES 16

static dom_actors_sim_state g_actor_states[DOM_ACTORS_MAX_SIM_STATES];
static uint32_t             g_actor_state_count = 0;

static dom_actors_sim_state* dom_actors_find_state(dom_instance_id inst)
{
    uint32_t i;

    for (i = 0u; i < g_actor_state_count; ++i) {
        if (g_actor_states[i].inst == inst) {
            return &g_actor_states[i];
        }
    }
    return NULL;
}

static dom_actors_sim_state* dom_actors_get_state(dom_instance_id inst)
{
    dom_actors_sim_state* state;

    state = dom_actors_find_state(inst);
    if (state) {
        return state;
    }
    if (g_actor_state_count >= DOM_ACTORS_MAX_SIM_STATES) {
        return NULL;
    }
    state = &g_actor_states[g_actor_state_count];
    state->inst = inst;
    state->step_count = 0u;
    g_actor_state_count += 1u;
    return state;
}

dom_status dom_actor_spawn(const dom_actor_spawn_desc* desc,
                           dom_actor_id* out_id)
{
    (void)desc;
    if (out_id) {
        *out_id = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actor_despawn(dom_actor_id id)
{
    (void)id;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actor_get_state(dom_actor_id id,
                               dom_actor_state* out_state,
                               size_t out_state_size)
{
    (void)id;
    if (out_state && out_state_size >= sizeof(dom_actor_state)) {
        out_state->struct_size      = (uint32_t)sizeof(dom_actor_state);
        out_state->struct_version   = 0;
        out_state->id               = 0;
        out_state->kind             = DOM_ACTOR_KIND_UNKNOWN;
        out_state->surface          = 0;
        out_state->life_support_mbar = 0;
        out_state->health_permille  = 0;
        out_state->flags            = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actor_tick(dom_actor_id id, uint32_t dt_millis)
{
    (void)id;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_actors_step(uint32_t dt_millis)
{
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_actors_sim_step(dom_core* core, dom_instance_id inst, double dt_s)
{
    dom_actors_sim_state* state;

    (void)core;
    (void)dt_s;

    state = dom_actors_get_state(inst);
    if (!state) {
        return;
    }
    state->step_count += 1u;
}

uint64_t dom_actors_debug_step_count(dom_instance_id inst)
{
    dom_actors_sim_state* state;

    state = dom_actors_find_state(inst);
    if (!state) {
        return 0u;
    }
    return state->step_count;
}
