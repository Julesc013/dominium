/*
FILE: game/rules/infrastructure/maintenance_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / infrastructure
RESPONSIBILITY: Implements deterministic maintenance state for machines.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Maintenance updates are deterministic.
*/
#include "dominium/rules/infrastructure/maintenance_model.h"

void maintenance_state_init(maintenance_state* state,
                            u32 max_level,
                            u32 min_operational)
{
    if (!state) {
        return;
    }
    state->max_level = max_level;
    state->min_operational = min_operational;
    state->level = max_level;
    state->next_due_tick = DOM_TIME_ACT_MAX;
}

int maintenance_is_operational(const maintenance_state* state)
{
    if (!state) {
        return 0;
    }
    return (state->level >= state->min_operational);
}

void maintenance_degrade(maintenance_state* state, u32 amount)
{
    if (!state || amount == 0u) {
        return;
    }
    if (amount >= state->level) {
        state->level = 0u;
    } else {
        state->level -= amount;
    }
}

void maintenance_service(maintenance_state* state, u32 amount)
{
    u32 next;
    if (!state || amount == 0u) {
        return;
    }
    next = state->level + amount;
    if (next > state->max_level) {
        next = state->max_level;
    }
    state->level = next;
}
