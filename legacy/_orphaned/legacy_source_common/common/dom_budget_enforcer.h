/*
FILE: source/dominium/common/dom_budget_enforcer.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_budget_enforcer
RESPONSIBILITY: Budget limits and enforcement state for non-authoritative work.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C89/C++98 headers.
FORBIDDEN DEPENDENCIES: OS headers; authoritative sim logic.
*/
#ifndef DOM_BUDGET_ENFORCER_H
#define DOM_BUDGET_ENFORCER_H

#include "domino/core/types.h"
#include "dom_profiler.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_BUDGET_LIMITS_VERSION = 1u,
    DOM_BUDGET_STATE_VERSION = 1u
};

enum {
    DOM_BUDGET_FIDELITY_MIN = 0u,
    DOM_BUDGET_FIDELITY_LOW = 1u,
    DOM_BUDGET_FIDELITY_MED = 2u,
    DOM_BUDGET_FIDELITY_HIGH = 3u
};

enum dom_budget_over_flags {
    DOM_BUDGET_OVER_SIM_TICK = 1u << 0,
    DOM_BUDGET_OVER_RENDER_SUBMIT = 1u << 1,
    DOM_BUDGET_OVER_DERIVED_MS = 1u << 2,
    DOM_BUDGET_OVER_DERIVED_IO = 1u << 3,
    DOM_BUDGET_OVER_DERIVED_JOBS = 1u << 4,
    DOM_BUDGET_OVER_SURFACE_CHUNKS = 1u << 5,
    DOM_BUDGET_OVER_ACTIVE_BUBBLES = 1u << 6
};

typedef struct dom_budget_limits {
    u32 struct_size;
    u32 struct_version;
    u32 perf_tier;
    u32 sim_tick_cost_ms_max;
    u32 derived_jobs_ms_per_frame_max;
    u32 derived_io_bytes_per_frame_max;
    u32 derived_jobs_per_frame_max;
    u32 render_submit_ms_max;
    u32 max_active_bubbles;
    u32 max_surface_chunks_active;
    u32 max_entities_per_bubble;
    u32 max_ai_ops_per_tick;
    u32 max_ai_factions_per_tick;
    u32 max_cosmo_entities_iterated_per_tick;
} dom_budget_limits;

typedef struct dom_budget_derived_sample {
    u32 last_pump_ms;
    u32 last_pump_io_bytes;
    u32 last_pump_jobs;
} dom_budget_derived_sample;

typedef struct dom_budget_state {
    u32 struct_size;
    u32 struct_version;
    u32 over_mask;
    u32 pressure;
    u32 fidelity_max;
    u32 derived_budget_ms;
    u32 derived_budget_io_bytes;
    u32 derived_budget_jobs;
    u32 ai_max_ops_per_tick;
    u32 ai_max_factions_per_tick;
    u32 max_active_bubbles;
    u32 max_surface_chunks_active;
    u32 max_entities_per_bubble;
    u32 max_cosmo_entities_iterated_per_tick;
} dom_budget_state;

typedef struct dom_budget_enforcer {
    dom_budget_limits limits;
    dom_budget_state state;
    u32 pressure;
    u32 base_derived_budget_ms;
    u32 base_derived_budget_io_bytes;
    u32 base_derived_budget_jobs;
} dom_budget_enforcer;

int dom_budget_limits_for_tier(u32 perf_tier, dom_budget_limits *out_limits);

int dom_budget_enforcer_init(dom_budget_enforcer *enforcer,
                             const dom_budget_limits *limits);
int dom_budget_enforcer_set_base_derived(dom_budget_enforcer *enforcer,
                                         u32 base_ms,
                                         u32 base_io_bytes,
                                         u32 base_jobs);
int dom_budget_enforcer_update(dom_budget_enforcer *enforcer,
                               const dom_profiler_frame *frame,
                               const dom_budget_derived_sample *derived,
                               u32 active_bubbles,
                               u32 active_surface_chunks);
int dom_budget_enforcer_get_state(const dom_budget_enforcer *enforcer,
                                  dom_budget_state *out_state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_BUDGET_ENFORCER_H */
