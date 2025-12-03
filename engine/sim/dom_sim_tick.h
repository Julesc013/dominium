#ifndef DOM_SIM_TICK_H
#define DOM_SIM_TICK_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_sim_time.h"

typedef enum DomSimPhase {
    DOM_SIM_PHASE_INPUT = 0,
    DOM_SIM_PHASE_PRE_STATE,
    DOM_SIM_PHASE_SIMULATION,
    DOM_SIM_PHASE_NETWORKS,
    DOM_SIM_PHASE_MERGE,
    DOM_SIM_PHASE_POST,
    DOM_SIM_PHASE_FINALIZE,
    DOM_SIM_PHASE_COUNT
} DomSimPhase;

#define DOM_SIM_MAX_LANES 8

typedef void (*DomSimPhaseFn)(dom_u32 lane_id, void *user);

typedef struct DomSimConfig {
    dom_u32 target_ups;
    dom_u32 num_lanes; /* 1..DOM_SIM_MAX_LANES */
} DomSimConfig;

dom_err_t dom_sim_tick_init(const DomSimConfig *cfg);
void      dom_sim_tick_set_phase_callback(DomSimPhase phase, DomSimPhaseFn fn, void *user);
dom_err_t dom_sim_tick_step(void);
DomSimTime dom_sim_tick_get_time(void);

#endif /* DOM_SIM_TICK_H */
