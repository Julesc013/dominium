#ifndef DOM_SIM_TIME_H
#define DOM_SIM_TIME_H

#include "dom_core_types.h"

typedef struct DomSimTime {
    dom_u64 tick;
    dom_u32 ups;  /* target UPS */
} DomSimTime;

void dom_sim_time_init(DomSimTime *t, dom_u32 ups);
void dom_sim_time_set_ups(DomSimTime *t, dom_u32 ups);
dom_u64 dom_sim_time_tick(const DomSimTime *t);
dom_u32 dom_sim_time_ups(const DomSimTime *t);

#endif /* DOM_SIM_TIME_H */
