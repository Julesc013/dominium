/*
FILE: include/dominium/rules/infrastructure/maintenance_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / infrastructure
RESPONSIBILITY: Defines deterministic maintenance state for machines.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Maintenance updates are deterministic.
*/
#ifndef DOMINIUM_RULES_INFRA_MAINTENANCE_MODEL_H
#define DOMINIUM_RULES_INFRA_MAINTENANCE_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct maintenance_state {
    u32 level;
    u32 max_level;
    u32 min_operational;
    dom_act_time_t next_due_tick;
} maintenance_state;

void maintenance_state_init(maintenance_state* state,
                            u32 max_level,
                            u32 min_operational);
int maintenance_is_operational(const maintenance_state* state);
void maintenance_degrade(maintenance_state* state, u32 amount);
void maintenance_service(maintenance_state* state, u32 amount);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_INFRA_MAINTENANCE_MODEL_H */
