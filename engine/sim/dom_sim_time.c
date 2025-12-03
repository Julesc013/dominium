#include "dom_sim_time.h"

void dom_sim_time_init(DomSimTime *t, dom_u32 ups)
{
    if (!t) return;
    t->tick = 0;
    t->ups = ups;
}

void dom_sim_time_set_ups(DomSimTime *t, dom_u32 ups)
{
    if (!t) return;
    t->ups = ups;
}

dom_u64 dom_sim_time_tick(const DomSimTime *t)
{
    return t ? t->tick : 0;
}

dom_u32 dom_sim_time_ups(const DomSimTime *t)
{
    return t ? t->ups : 0;
}
