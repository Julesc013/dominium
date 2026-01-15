/*
FILE: source/domino/sim/_legacy/core_sim/dom_sim_tick.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/dom_sim_tick
RESPONSIBILITY: Implements `dom_sim_tick`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_sim_tick.h"

typedef struct DomSimPhaseHandler {
    DomSimPhaseFn phase_fn;
    DomSimLaneFn  lane_fn;
    void         *user;
} DomSimPhaseHandler;

const dom_u32 DOM_SIM_CANONICAL_UPS[DOM_SIM_CANONICAL_UPS_COUNT] = {
    1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240, 500, 1000
};

static DomSimTime g_time;
static DomSimConfig g_cfg;
static DomSimPhaseHandler g_handlers[DOM_SIM_PHASE_COUNT];

static dom_bool8 dom_sim_tick_is_canonical(dom_u32 ups)
{
    dom_u32 i;
    for (i = 0; i < DOM_SIM_CANONICAL_UPS_COUNT; ++i) {
        if (DOM_SIM_CANONICAL_UPS[i] == ups) return 1;
    }
    return 0;
}

static void dom_sim_tick_reset_handlers(void)
{
    dom_u32 i;
    for (i = 0; i < DOM_SIM_PHASE_COUNT; ++i) {
        g_handlers[i].phase_fn = 0;
        g_handlers[i].lane_fn = 0;
        g_handlers[i].user = 0;
    }
}

dom_err_t dom_sim_tick_init(const DomSimConfig *cfg)
{
    if (!cfg) return DOM_ERR_INVALID_ARG;
    g_cfg = *cfg;
    if (g_cfg.num_lanes == 0 || g_cfg.num_lanes > DOM_SIM_MAX_LANES) {
        g_cfg.num_lanes = 1;
    }
    if (!dom_sim_tick_is_canonical(g_cfg.target_ups)) {
        return DOM_ERR_INVALID_ARG;
    }
    dom_sim_time_init(&g_time, g_cfg.target_ups);
    dom_sim_tick_reset_handlers();
    return DOM_OK;
}

void dom_sim_tick_reset(DomTickId start_tick)
{
    dom_sim_time_reset(&g_time, start_tick);
}

dom_err_t dom_sim_tick_set_phase_handler(DomSimPhase phase,
                                         DomSimPhaseFn phase_fn,
                                         DomSimLaneFn lane_fn,
                                         void *user_data)
{
    if (phase >= DOM_SIM_PHASE_COUNT) return DOM_ERR_INVALID_ARG;
    g_handlers[phase].phase_fn = phase_fn;
    g_handlers[phase].lane_fn = lane_fn;
    g_handlers[phase].user = user_data;
    return DOM_OK;
}

static void dom_sim_tick_run_handler(DomSimPhase phase)
{
    DomSimPhaseHandler *h = &g_handlers[phase];
    dom_u32 lane;
    if (h->phase_fn) {
        h->phase_fn(h->user);
    }
    if (h->lane_fn) {
        for (lane = 0; lane < g_cfg.num_lanes; ++lane) {
            h->lane_fn((DomLaneId)lane, h->user);
        }
    }
}

dom_err_t dom_sim_tick_step(void)
{
    dom_sim_phase_input();
    dom_sim_phase_pre_state();
    dom_sim_phase_simulation();
    dom_sim_phase_networks();
    dom_sim_phase_merge();
    dom_sim_phase_post_process();
    dom_sim_phase_finalize();
    g_time.tick += 1;
    return DOM_OK;
}

DomTickId dom_sim_tick_current(void)
{
    return g_time.tick;
}

DomSimTime dom_sim_tick_get_time(void)
{
    return g_time;
}

dom_err_t dom_sim_tick_set_effective_ups(dom_u32 ups)
{
    if (!dom_sim_tick_is_canonical(ups)) return DOM_ERR_INVALID_ARG;
    dom_sim_time_set_effective_ups(&g_time, ups);
    return DOM_OK;
}

dom_u32 dom_sim_tick_get_effective_ups(void)
{
    return dom_sim_time_effective_ups(&g_time);
}

DomLaneId dom_sim_tick_lane_for_entity(dom_entity_id entity)
{
    dom_u32 lane_count = g_cfg.num_lanes ? g_cfg.num_lanes : 1;
    dom_u32 idx = dom_entity_index(entity);
    return (DomLaneId)(idx % lane_count);
}

dom_u32 dom_sim_tick_lane_count(void)
{
    return g_cfg.num_lanes ? g_cfg.num_lanes : 1;
}

void dom_sim_phase_input(void)
{
    dom_sim_tick_run_handler(DOM_SIM_PHASE_INPUT);
}

void dom_sim_phase_pre_state(void)
{
    dom_sim_tick_run_handler(DOM_SIM_PHASE_PRE_STATE);
}

void dom_sim_phase_simulation(void)
{
    dom_sim_tick_run_handler(DOM_SIM_PHASE_SIMULATION);
}

void dom_sim_phase_networks(void)
{
    dom_sim_tick_run_handler(DOM_SIM_PHASE_NETWORKS);
}

void dom_sim_phase_merge(void)
{
    dom_sim_tick_run_handler(DOM_SIM_PHASE_MERGE);
}

void dom_sim_phase_post_process(void)
{
    dom_sim_tick_run_handler(DOM_SIM_PHASE_POST_PROCESS);
}

void dom_sim_phase_finalize(void)
{
    dom_sim_tick_run_handler(DOM_SIM_PHASE_FINALIZE);
}
