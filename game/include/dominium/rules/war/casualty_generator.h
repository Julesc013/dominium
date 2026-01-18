/*
FILE: include/dominium/rules/war/casualty_generator.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic casualty generation via LIFE2 pipelines.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Casualty generation order is deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_CASUALTY_GENERATOR_H
#define DOMINIUM_RULES_WAR_CASUALTY_GENERATOR_H

#include "dominium/life/death_pipeline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct casualty_source {
    const u64* body_ids;
    u32 count;
    u32 cursor;
} casualty_source;

typedef struct casualty_request {
    u32 cause_code;
    dom_act_time_t act_time;
    u64 location_ref;
    u64 provenance_ref;
    u32 policy_id;
    dom_account_id_t remains_inventory_account_id;
    u64 jurisdiction_id;
    u8 has_contract;
    u8 allow_finder;
    u8 jurisdiction_allows;
    u8 estate_locked;
    u8 collapse_remains;
} casualty_request;

typedef struct casualty_generator {
    life_death_context* life;
} casualty_generator;

int casualty_generate(casualty_generator* gen,
                      casualty_source* source,
                      u32 casualty_count,
                      const casualty_request* req,
                      u64* out_death_event_ids,
                      u32 out_capacity,
                      u32* out_count,
                      life_death_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_CASUALTY_GENERATOR_H */
