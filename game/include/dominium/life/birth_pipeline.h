/*
FILE: include/dominium/life/birth_pipeline.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines LIFE3 birth pipeline entrypoint and scheduling.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pipeline ordering and IDs are deterministic.
*/
#ifndef DOMINIUM_LIFE_BIRTH_PIPELINE_H
#define DOMINIUM_LIFE_BIRTH_PIPELINE_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/life/birth_event.h"
#include "dominium/life/birth_refusal_codes.h"
#include "dominium/life/cohort_update_hooks.h"
#include "dominium/life/death_pipeline.h"
#include "dominium/life/gestation_state.h"
#include "dominium/life/lineage.h"
#include "dominium/life/life_audit_log.h"
#include "dominium/life/control_authority.h"
#include "dominium/rules/needs_constraints.h"
#include "dominium/rules/reproduction_rules.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_birth_notice {
    u64 birth_event_id;
    u64 child_person_id;
    u32 parent_count;
    u64 parent_ids[2];
    dom_act_time_t act_time_of_birth;
    u64 location_ref;
} life_birth_notice;

typedef void (*life_birth_notice_cb)(void* user, const life_birth_notice* notice);

typedef struct life_id_gen {
    u64 next_id;
} life_id_gen;

void life_id_gen_init(life_id_gen* gen, u64 start_id);
int life_id_next(life_id_gen* gen, u64* out_id);

typedef struct life_birth_request {
    u64 parent_ids[2];
    u32 parent_count;
    u32 parent_certainty[2];
    dom_act_time_t act_time;
    u64 location_ref;
    u64 provenance_ref;
    u64 cohort_id;
    u8 micro_active;
    u64 controller_id;
    life_need_snapshot needs;
} life_birth_request;

typedef struct life_birth_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    struct life_birth_due_user* due_users;
    life_gestation_registry* gestations;
    life_birth_event_list* births;
    life_lineage_registry* lineage;
    life_cohort_registry* cohorts;
    life_person_registry* persons;
    life_body_registry* bodies;
    life_id_gen* person_ids;
    life_id_gen* body_ids;
    life_audit_log* audit_log;
    life_birth_notice_cb notice_cb;
    void* notice_user;
} life_birth_scheduler;

typedef struct life_birth_due_user {
    life_birth_scheduler* scheduler;
    life_gestation_state* gestation;
} life_birth_due_user;

typedef struct life_birth_context {
    life_gestation_registry* gestations;
    life_birth_scheduler* scheduler;
    life_birth_event_list* births;
    life_lineage_registry* lineage;
    life_cohort_registry* cohorts;
    life_person_registry* persons;
    life_body_registry* bodies;
    life_id_gen* person_ids;
    life_id_gen* body_ids;
    life_audit_log* audit_log;
    const life_reproduction_rules* reproduction_rules;
    const life_authority_set* authority;
    life_birth_notice_cb notice_cb;
    void* notice_user;
} life_birth_context;

int life_birth_scheduler_init(life_birth_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              life_birth_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              life_gestation_registry* gestations,
                              life_birth_event_list* births,
                              life_lineage_registry* lineage,
                              life_cohort_registry* cohorts,
                              life_person_registry* persons,
                              life_body_registry* bodies,
                              life_id_gen* person_ids,
                              life_id_gen* body_ids,
                              life_audit_log* audit_log,
                              life_birth_notice_cb notice_cb,
                              void* notice_user);

int life_birth_scheduler_register(life_birth_scheduler* sched,
                                  life_gestation_state* gestation);

int life_birth_scheduler_advance(life_birth_scheduler* sched,
                                 dom_act_time_t target_tick);

int life_request_birth(life_birth_context* ctx,
                       const life_birth_request* request,
                       life_birth_refusal_code* out_refusal,
                       u64* out_gestation_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_BIRTH_PIPELINE_H */
