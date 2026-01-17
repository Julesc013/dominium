/*
FILE: include/dominium/life/death_pipeline.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines LIFE2 death pipeline entrypoint and supporting registries.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pipeline ordering and IDs are deterministic.
*/
#ifndef DOMINIUM_LIFE_DEATH_PIPELINE_H
#define DOMINIUM_LIFE_DEATH_PIPELINE_H

#include "dominium/life/death_event.h"
#include "dominium/life/estate.h"
#include "dominium/life/inheritance_scheduler.h"
#include "dominium/life/life_audit_log.h"
#include "dominium/life/life_refusal_codes.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_body_state {
    LIFE_BODY_ALIVE = 1,
    LIFE_BODY_DEAD = 2,
    LIFE_BODY_MISSING = 3
} life_body_state;

typedef struct life_body_record {
    u64 body_id;
    u64 person_id;
    u32 alive_state;
} life_body_record;

typedef struct life_body_registry {
    life_body_record* bodies;
    u32 count;
    u32 capacity;
} life_body_registry;

typedef struct life_person_record {
    u64 person_id;
} life_person_record;

typedef struct life_person_registry {
    life_person_record* persons;
    u32 count;
    u32 capacity;
} life_person_registry;

typedef struct life_death_notice {
    u64 death_event_id;
    u64 body_id;
    u64 person_id;
    u32 cause_code;
    dom_act_time_t act_time_of_death;
    u64 location_ref;
} life_death_notice;

typedef void (*life_death_notice_cb)(void* user, const life_death_notice* notice);

typedef struct life_death_input {
    u64 body_id;
    u32 cause_code;
    dom_act_time_t act_time;
    u64 location_ref;
    u64 provenance_ref;
    u32 policy_id;
} life_death_input;

typedef struct life_death_context {
    life_body_registry* bodies;
    life_person_registry* persons;
    life_person_account_registry* person_accounts;
    life_account_owner_registry* account_owners;
    life_death_event_list* death_events;
    life_estate_registry* estates;
    life_inheritance_scheduler* scheduler;
    life_audit_log* audit_log;
    dom_ledger* ledger;
    life_death_notice_cb notice_cb;
    void* notice_user;
} life_death_context;

void life_body_registry_init(life_body_registry* reg,
                             life_body_record* storage,
                             u32 capacity);
int life_body_register(life_body_registry* reg,
                       u64 body_id,
                       u64 person_id,
                       u32 alive_state);
life_body_record* life_body_find(life_body_registry* reg, u64 body_id);

void life_person_registry_init(life_person_registry* reg,
                               life_person_record* storage,
                               u32 capacity);
int life_person_register(life_person_registry* reg, u64 person_id);
int life_person_exists(const life_person_registry* reg, u64 person_id);

int life_handle_death(life_death_context* ctx,
                      const life_death_input* input,
                      life_death_refusal_code* out_refusal,
                      u64* out_death_event_id,
                      u64* out_estate_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_DEATH_PIPELINE_H */
