/*
FILE: include/dominium/rules/population/population_projections.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / population rules
RESPONSIBILITY: Defines epistemic population projections (known vs unknown).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Projections update deterministically.
*/
#ifndef DOMINIUM_RULES_POPULATION_PROJECTIONS_H
#define DOMINIUM_RULES_POPULATION_PROJECTIONS_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct population_projection {
    u64 cohort_id;
    u32 known_min;
    u32 known_max;
    dom_act_time_t report_tick;
    int is_known;
} population_projection;

typedef struct population_projection_registry {
    population_projection* projections;
    u32 count;
    u32 capacity;
} population_projection_registry;

void population_projection_registry_init(population_projection_registry* reg,
                                         population_projection* storage,
                                         u32 capacity);
int population_projection_report(population_projection_registry* reg,
                                 u64 cohort_id,
                                 u32 known_min,
                                 u32 known_max,
                                 dom_act_time_t report_tick);
int population_projection_get(const population_projection_registry* reg,
                              u64 cohort_id,
                              population_projection* out_view);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_POPULATION_PROJECTIONS_H */
