/*
FILE: include/dominium/rules/war/territory_control.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic territory control records and estimates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Territory control ordering and updates are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_TERRITORY_CONTROL_H
#define DOMINIUM_RULES_WAR_TERRITORY_CONTROL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/epistemic.h"

#ifdef __cplusplus
extern "C" {
#endif

#define TERRITORY_CONTROL_SCALE 1000u

typedef struct territory_control {
    u64 territory_id;
    u64 current_controller;
    u32 contested_flag;
    u32 control_strength;
    dom_act_time_t next_due_tick;
} territory_control;

typedef struct territory_control_registry {
    territory_control* controls;
    u32 count;
    u32 capacity;
} territory_control_registry;

typedef struct territory_control_estimate {
    u64 controller_id;
    u32 control_strength;
    u32 contested_flag;
    u32 uncertainty_q16;
    int is_exact;
} territory_control_estimate;

void territory_control_registry_init(territory_control_registry* reg,
                                     territory_control* storage,
                                     u32 capacity);
territory_control* territory_control_find(territory_control_registry* reg,
                                          u64 territory_id);
int territory_control_register(territory_control_registry* reg,
                               u64 territory_id,
                               u64 controller_id,
                               u32 control_strength);
int territory_control_set_controller(territory_control_registry* reg,
                                     u64 territory_id,
                                     u64 controller_id,
                                     u32 control_strength);
int territory_control_apply_delta(territory_control_registry* reg,
                                  u64 territory_id,
                                  i32 delta);
int territory_control_set_contested(territory_control_registry* reg,
                                    u64 territory_id,
                                    u32 contested_flag);

int territory_control_estimate_from_view(const dom_epistemic_view* view,
                                         const territory_control* actual,
                                         territory_control_estimate* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_TERRITORY_CONTROL_H */
