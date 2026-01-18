/*
FILE: include/dominium/sim/macro_due_scheduler_hooks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / sim
RESPONSIBILITY: Defines minimal macro due-scheduler hooks for survival subsystems.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation is deterministic.
*/
#ifndef DOMINIUM_SIM_MACRO_DUE_SCHEDULER_HOOKS_H
#define DOMINIUM_SIM_MACRO_DUE_SCHEDULER_HOOKS_H

#include "domino/core/dom_time_core.h"
#include "dominium/rules/survival/consumption_scheduler.h"
#include "dominium/rules/survival/survival_production_actions.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_macro_due_hooks {
    survival_consumption_scheduler* consumption;
    survival_production_scheduler* production;
} dom_macro_due_hooks;

dom_act_time_t dom_macro_next_due(const dom_macro_due_hooks* hooks);
int dom_macro_process_until(dom_macro_due_hooks* hooks, dom_act_time_t target_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SIM_MACRO_DUE_SCHEDULER_HOOKS_H */
