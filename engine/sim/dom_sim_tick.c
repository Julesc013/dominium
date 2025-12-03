#include "dom_sim_tick.h"

static DomSimTime g_time;
static DomSimConfig g_cfg;
static DomSimPhaseFn g_phase_fn[DOM_SIM_PHASE_COUNT];
static void *g_phase_ud[DOM_SIM_PHASE_COUNT];

dom_err_t dom_sim_tick_init(const DomSimConfig *cfg)
{
    dom_u32 i;
    if (!cfg) return DOM_ERR_INVALID_ARG;
    g_cfg = *cfg;
    if (g_cfg.num_lanes == 0 || g_cfg.num_lanes > DOM_SIM_MAX_LANES) g_cfg.num_lanes = 1;
    dom_sim_time_init(&g_time, g_cfg.target_ups);
    for (i = 0; i < DOM_SIM_PHASE_COUNT; ++i) {
        g_phase_fn[i] = 0;
        g_phase_ud[i] = 0;
    }
    return DOM_OK;
}

void dom_sim_tick_set_phase_callback(DomSimPhase phase, DomSimPhaseFn fn, void *user)
{
    if (phase >= DOM_SIM_PHASE_COUNT) return;
    g_phase_fn[phase] = fn;
    g_phase_ud[phase] = user;
}

static void dom_sim_tick_run_phase(DomSimPhase phase)
{
    DomSimPhaseFn fn = g_phase_fn[phase];
    void *ud = g_phase_ud[phase];
    dom_u32 lane;
    if (!fn) return;
    for (lane = 0; lane < g_cfg.num_lanes; ++lane) {
        fn(lane, ud);
    }
}

dom_err_t dom_sim_tick_step(void)
{
    dom_sim_tick_run_phase(DOM_SIM_PHASE_INPUT);
    dom_sim_tick_run_phase(DOM_SIM_PHASE_PRE_STATE);
    dom_sim_tick_run_phase(DOM_SIM_PHASE_SIMULATION);
    dom_sim_tick_run_phase(DOM_SIM_PHASE_NETWORKS);
    dom_sim_tick_run_phase(DOM_SIM_PHASE_MERGE);
    dom_sim_tick_run_phase(DOM_SIM_PHASE_POST);
    dom_sim_tick_run_phase(DOM_SIM_PHASE_FINALIZE);

    g_time.tick += 1;
    return DOM_OK;
}

DomSimTime dom_sim_tick_get_time(void)
{
    return g_time;
}
