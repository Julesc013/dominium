/*
FILE: game/core/sim/macro_due_scheduler_hooks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / sim
RESPONSIBILITY: Implements macro due-scheduler hooks for survival and population subsystems.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation is deterministic.
*/
#include "dominium/sim/macro_due_scheduler_hooks.h"

static dom_act_time_t dom_macro_min_due(dom_act_time_t a, dom_act_time_t b)
{
    if (a == DG_DUE_TICK_NONE) {
        return b;
    }
    if (b == DG_DUE_TICK_NONE) {
        return a;
    }
    return (a < b) ? a : b;
}

dom_act_time_t dom_macro_next_due(const dom_macro_due_hooks* hooks)
{
    dom_act_time_t next = DG_DUE_TICK_NONE;
    if (!hooks) {
        return DG_DUE_TICK_NONE;
    }
    if (hooks->consumption) {
        next = dom_macro_min_due(next, survival_consumption_next_due(hooks->consumption));
    }
    if (hooks->production) {
        next = dom_macro_min_due(next, survival_production_next_due(hooks->production));
    }
    if (hooks->population) {
        next = dom_macro_min_due(next, population_scheduler_next_due(hooks->population));
    }
    return next;
}

int dom_macro_process_until(dom_macro_due_hooks* hooks, dom_act_time_t target_tick)
{
    if (!hooks) {
        return -1;
    }
    if (hooks->consumption) {
        if (survival_consumption_advance(hooks->consumption, target_tick) != 0) {
            return -2;
        }
    }
    if (hooks->production) {
        if (survival_production_advance(hooks->production, target_tick) != 0) {
            return -3;
        }
    }
    if (hooks->population) {
        if (population_scheduler_advance(hooks->population, target_tick) != 0) {
            return -4;
        }
    }
    return 0;
}
