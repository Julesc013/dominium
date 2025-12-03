#ifndef DOM_SIM_TICK_H
#define DOM_SIM_TICK_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"
#include "dom_sim_time.h"

typedef enum DomSimPhase {
    DOM_SIM_PHASE_INPUT = 0,
    DOM_SIM_PHASE_PRE_STATE,
    DOM_SIM_PHASE_SIMULATION,
    DOM_SIM_PHASE_NETWORKS,
    DOM_SIM_PHASE_MERGE,
    DOM_SIM_PHASE_POST_PROCESS,
    DOM_SIM_PHASE_FINALIZE,
    DOM_SIM_PHASE_COUNT
} DomSimPhase;

/* Deterministic virtual lanes */
typedef dom_u32 DomLaneId;

/* Canonical UPS set from SPEC_CORE */
#define DOM_SIM_CANONICAL_UPS_COUNT 14
extern const dom_u32 DOM_SIM_CANONICAL_UPS[DOM_SIM_CANONICAL_UPS_COUNT];

#define DOM_SIM_MAX_LANES 8

typedef struct DomSimConfig {
    dom_u32 target_ups;           /* canonical UPS */
    dom_u32 num_lanes;            /* virtual lane count */
    dom_u32 reserved[6];          /* future-proofing */
} DomSimConfig;

typedef void (*DomSimPhaseFn)(void *user_data);
typedef void (*DomSimLaneFn)(DomLaneId lane_id, void *user_data);

dom_err_t dom_sim_tick_init(const DomSimConfig *cfg);
void      dom_sim_tick_reset(DomTickId start_tick);
dom_err_t dom_sim_tick_set_phase_handler(DomSimPhase phase,
                                         DomSimPhaseFn phase_fn,
                                         DomSimLaneFn lane_fn,
                                         void *user_data);

dom_err_t dom_sim_tick_step(void);
DomTickId dom_sim_tick_current(void);
DomSimTime dom_sim_tick_get_time(void);

dom_err_t dom_sim_tick_set_effective_ups(dom_u32 ups);
dom_u32   dom_sim_tick_get_effective_ups(void);

DomLaneId dom_sim_tick_lane_for_entity(dom_entity_id entity);
dom_u32   dom_sim_tick_lane_count(void);

/* Phase entry points (called only by dom_sim_tick_step) */
void dom_sim_phase_input(void);
void dom_sim_phase_pre_state(void);
void dom_sim_phase_simulation(void);
void dom_sim_phase_networks(void);
void dom_sim_phase_merge(void);
void dom_sim_phase_post_process(void);
void dom_sim_phase_finalize(void);

#endif /* DOM_SIM_TICK_H */
