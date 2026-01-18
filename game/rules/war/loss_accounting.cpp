/*
FILE: game/rules/war/loss_accounting.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic loss accounting helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Loss application is deterministic.
*/
#include "dominium/rules/war/loss_accounting.h"

int loss_accounting_apply_equipment_losses(security_force* force,
                                           const engagement_equipment_loss* losses,
                                           u32 loss_count)
{
    u32 i;
    u32 j;
    if (!force || !losses) {
        return -1;
    }
    for (i = 0u; i < loss_count; ++i) {
        u64 equipment_id = losses[i].equipment_id;
        u32 loss_qty = losses[i].qty;
        if (equipment_id == 0u || loss_qty == 0u) {
            continue;
        }
        for (j = 0u; j < force->equipment_count; ++j) {
            if (force->equipment_refs[j] == equipment_id) {
                if (force->equipment_qtys[j] <= loss_qty) {
                    force->equipment_qtys[j] = 0u;
                } else {
                    force->equipment_qtys[j] -= loss_qty;
                }
                break;
            }
        }
    }
    return 0;
}

int loss_accounting_apply_readiness(readiness_registry* registry,
                                    u64 readiness_id,
                                    i32 delta,
                                    dom_act_time_t act_time)
{
    readiness_state* state;
    if (!registry || readiness_id == 0u) {
        return -1;
    }
    state = readiness_find(registry, readiness_id);
    if (!state) {
        return -2;
    }
    return readiness_apply_delta(state, delta, act_time);
}

int loss_accounting_apply_morale(morale_registry* registry,
                                 u64 morale_id,
                                 i32 delta)
{
    morale_state* state;
    if (!registry || morale_id == 0u) {
        return -1;
    }
    state = morale_find(registry, morale_id);
    if (!state) {
        return -2;
    }
    return morale_apply_delta(state, delta);
}

int loss_accounting_apply_legitimacy(legitimacy_registry* registry,
                                     u64 legitimacy_id,
                                     i32 delta)
{
    legitimacy_state* state;
    if (!registry || legitimacy_id == 0u) {
        return -1;
    }
    state = legitimacy_find(registry, legitimacy_id);
    if (!state) {
        return -2;
    }
    return legitimacy_apply_delta(state, delta);
}
