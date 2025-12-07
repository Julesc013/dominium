#include "dom_sim_time.h"

void dom_sim_time_init(DomSimTime *t, dom_u32 target_ups)
{
    if (!t) return;
    t->tick = 0;
    t->target_ups = target_ups;
    t->effective_ups = target_ups;
}

void dom_sim_time_reset(DomSimTime *t, DomTickId start_tick)
{
    if (!t) return;
    t->tick = start_tick;
}

void dom_sim_time_set_effective_ups(DomSimTime *t, dom_u32 ups)
{
    if (!t) return;
    t->effective_ups = ups;
}

DomTickId dom_sim_time_tick(const DomSimTime *t)
{
    return t ? t->tick : 0;
}

dom_u32 dom_sim_time_target_ups(const DomSimTime *t)
{
    return t ? t->target_ups : 0;
}

dom_u32 dom_sim_time_effective_ups(const DomSimTime *t)
{
    return t ? t->effective_ups : 0;
}
