/*
FILE: include/dominium/rules/city/city_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / city rules
RESPONSIBILITY: Defines city records and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: City ordering is stable and deterministic.
*/
#ifndef DOMINIUM_RULES_CITY_MODEL_H
#define DOMINIUM_RULES_CITY_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/city/city_refusal_codes.h"
#include "dominium/rules/infrastructure/building_machine.h"
#include "dominium/rules/infrastructure/store_model.h"

#ifdef __cplusplus
extern "C" {
#endif

#define CITY_MAX_BUILDINGS 64u
#define CITY_MAX_COHORT_REFS 32u
#define CITY_MAX_SUMMARY_ASSETS 16u

typedef struct city_macro_asset_total {
    u64 asset_id;
    u32 qty;
} city_macro_asset_total;

typedef struct city_macro_summary {
    city_macro_asset_total totals[CITY_MAX_SUMMARY_ASSETS];
    u32 total_count;
} city_macro_summary;

typedef struct city_record {
    u64 city_id;
    u64 location_ref;
    u64 boundary_ref;
    u64 governance_context_ref;
    u64 building_ids[CITY_MAX_BUILDINGS];
    u32 building_count;
    u64 population_cohort_refs[CITY_MAX_COHORT_REFS];
    u32 cohort_count;
    dom_act_time_t next_due_tick;
} city_record;

typedef struct city_registry {
    city_record* cities;
    u32 count;
    u32 capacity;
} city_registry;

void city_registry_init(city_registry* reg,
                        city_record* storage,
                        u32 capacity);
int city_register(city_registry* reg,
                  u64 city_id,
                  u64 location_ref,
                  u64 governance_context_ref);
city_record* city_find(city_registry* reg, u64 city_id);
int city_add_building(city_registry* reg,
                      u64 city_id,
                      u64 building_id,
                      civ1_refusal_code* out_refusal);
int city_add_population_cohort(city_registry* reg,
                               u64 city_id,
                               u64 cohort_id,
                               civ1_refusal_code* out_refusal);

int city_collect_macro_summary(const city_record* city,
                               const building_machine_registry* machines,
                               const infra_store_registry* stores,
                               city_macro_summary* out_summary);
int city_apply_macro_summary(const city_record* city,
                             const building_machine_registry* machines,
                             infra_store_registry* stores,
                             const city_macro_summary* summary);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_CITY_MODEL_H */
