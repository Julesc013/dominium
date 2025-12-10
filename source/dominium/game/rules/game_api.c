#include "dominium/game_api.h"
#include "dominium/world.h"
#include "dominium/constructions.h"
#include "dominium/actors.h"

typedef struct dom_game_sim_pipeline_state {
    dom_instance_id inst;
    uint64_t        game_steps;
    uint64_t        network_steps;
    uint64_t        environment_steps;
} dom_game_sim_pipeline_state;

#define DOM_GAME_SIM_MAX_STATES 16
#define DOM_GAME_SIM_STEP_ARGS_VERSION 1u

static dom_game_sim_pipeline_state g_game_sim_states[DOM_GAME_SIM_MAX_STATES];
static uint32_t                    g_game_sim_state_count = 0;

static dom_game_sim_pipeline_state* dom_game_find_sim_state(dom_instance_id inst)
{
    uint32_t i;

    for (i = 0u; i < g_game_sim_state_count; ++i) {
        if (g_game_sim_states[i].inst == inst) {
            return &g_game_sim_states[i];
        }
    }
    return NULL;
}

static dom_game_sim_pipeline_state* dom_game_get_sim_state(dom_instance_id inst)
{
    dom_game_sim_pipeline_state* state;

    state = dom_game_find_sim_state(inst);
    if (state) {
        return state;
    }
    if (g_game_sim_state_count >= DOM_GAME_SIM_MAX_STATES) {
        return NULL;
    }
    state = &g_game_sim_states[g_game_sim_state_count];
    state->inst = inst;
    state->game_steps = 0u;
    state->network_steps = 0u;
    state->environment_steps = 0u;
    g_game_sim_state_count += 1u;
    return state;
}

static void dom_game_networks_sim_step(dom_core* core,
                                       dom_instance_id inst,
                                       double dt_s,
                                       dom_game_sim_pipeline_state* pipeline)
{
    (void)core;
    (void)inst;
    (void)dt_s;

    if (pipeline) {
        pipeline->network_steps += 1u;
    }
}

static void dom_game_environment_sim_step(dom_core* core,
                                          dom_instance_id inst,
                                          double dt_s,
                                          dom_game_sim_pipeline_state* pipeline)
{
    (void)core;
    (void)inst;
    (void)dt_s;

    if (pipeline) {
        pipeline->environment_steps += 1u;
    }
}

struct dom_game_runtime {
    const dom_game_runtime_desc* desc;
};

dom_status dom_game_runtime_create(const dom_game_runtime_desc* desc,
                                   dom_game_runtime** out_runtime)
{
    (void)desc;
    (void)out_runtime;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_game_runtime_destroy(dom_game_runtime* runtime)
{
    (void)runtime;
}

dom_status dom_game_runtime_tick(dom_game_runtime* runtime, uint32_t dt_millis)
{
    (void)runtime;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_game_runtime_execute(dom_game_runtime* runtime,
                                    const dom_game_command* cmd)
{
    (void)runtime;
    (void)cmd;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_game_runtime_query(dom_game_runtime* runtime,
                                  const dom_game_query* query,
                                  void* response_buffer,
                                  size_t response_buffer_size)
{
    (void)runtime;
    (void)query;
    (void)response_buffer;
    (void)response_buffer_size;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_game_sim_step(dom_core* core, const dom_game_sim_step_args* args)
{
    dom_game_sim_pipeline_state* pipeline;

    if (!args ||
        args->struct_size != sizeof(dom_game_sim_step_args) ||
        args->struct_version != DOM_GAME_SIM_STEP_ARGS_VERSION) {
        return;
    }

    pipeline = dom_game_get_sim_state(args->inst);
    if (pipeline) {
        pipeline->game_steps += 1u;
    }

    /* Subsystem order is deterministic and fixed for now */
    dom_world_sim_step(core, args->inst, args->dt_s);
    dom_constructions_sim_step(core, args->inst, args->dt_s);
    dom_actors_sim_step(core, args->inst, args->dt_s);
    dom_game_networks_sim_step(core, args->inst, args->dt_s, pipeline);
    dom_game_environment_sim_step(core, args->inst, args->dt_s, pipeline);
}

uint64_t dom_game_debug_sim_steps(dom_instance_id inst)
{
    dom_game_sim_pipeline_state* state;

    state = dom_game_find_sim_state(inst);
    if (!state) {
        return 0u;
    }
    return state->game_steps;
}
