#ifndef DOM_SIM_TIME_H
#define DOM_SIM_TIME_H

#include "dom_core_types.h"

/* Deterministic tick identifier */
typedef dom_u64 DomTickId;

typedef struct DomSimTime {
    DomTickId tick;       /* current tick id */
    dom_u32   target_ups; /* configured UPS target */
    dom_u32   effective_ups; /* effective UPS (degraded under load) */
} DomSimTime;

void      dom_sim_time_init(DomSimTime *t, dom_u32 target_ups);
void      dom_sim_time_reset(DomSimTime *t, DomTickId start_tick);
void      dom_sim_time_set_effective_ups(DomSimTime *t, dom_u32 ups);
DomTickId dom_sim_time_tick(const DomSimTime *t);
dom_u32   dom_sim_time_target_ups(const DomSimTime *t);
dom_u32   dom_sim_time_effective_ups(const DomSimTime *t);

#endif /* DOM_SIM_TIME_H */
