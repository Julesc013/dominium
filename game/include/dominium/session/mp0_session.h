/*
FILE: include/dominium/session/mp0_session.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / session
RESPONSIBILITY: Defines MP0 loopback/lockstep/server-auth parity harness.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: State transitions are deterministic and replayable.
*/
#ifndef DOMINIUM_SESSION_MP0_SESSION_H
#define DOMINIUM_SESSION_MP0_SESSION_H

#include "domino/core/dom_ledger.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/life/controller_binding.h"
#include "dominium/life/death_event.h"
#include "dominium/life/death_pipeline.h"
#include "dominium/life/estate.h"
#include "dominium/life/inheritance_scheduler.h"
#include "dominium/life/life_audit_log.h"
#include "dominium/life/life_events_stub.h"
#include "dominium/life/remains.h"
#include "dominium/life/remains_decay_scheduler.h"
#include "dominium/life/rights_post_death.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/consumption_scheduler.h"
#include "dominium/rules/survival/needs_model.h"
#include "dominium/rules/survival/survival_production_actions.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_MP0_MAX_COHORTS 8u
#define DOM_MP0_MAX_ACTIONS 16u
#define DOM_MP0_MAX_PERSONS 8u
#define DOM_MP0_MAX_ACCOUNTS 8u
#define DOM_MP0_MAX_DEATH_EVENTS 8u
#define DOM_MP0_MAX_ESTATES 8u
#define DOM_MP0_MAX_INHERIT_ACTIONS 8u
#define DOM_MP0_MAX_REMAINS 8u
#define DOM_MP0_MAX_RIGHTS 8u
#define DOM_MP0_MAX_COMMANDS 32u

typedef enum dom_mp0_mode {
    DOM_MP0_MODE_LOOPBACK = 1,
    DOM_MP0_MODE_LOCKSTEP = 2,
    DOM_MP0_MODE_SERVER_AUTH = 3
} dom_mp0_mode;

typedef enum dom_mp0_command_type {
    DOM_MP0_CMD_PRODUCTION = 1,
    DOM_MP0_CMD_CONTINUATION = 2
} dom_mp0_command_type;

typedef struct dom_mp0_command {
    u32 type;
    dom_act_time_t tick;
    u32 sequence;
    union {
        survival_production_action_input production;
        life_cmd_continuation_select continuation;
    } data;
} dom_mp0_command;

typedef struct dom_mp0_command_queue {
    dom_mp0_command* commands;
    u32 count;
    u32 capacity;
    u32 next_sequence;
} dom_mp0_command_queue;

typedef struct dom_mp0_cohort_binding {
    u64 cohort_id;
    u64 person_id;
    u64 body_id;
    u64 location_ref;
    dom_account_id_t account_id;
} dom_mp0_cohort_binding;

typedef struct dom_mp0_state {
    dom_act_time_t now_tick;
    u32 policy_id;

    survival_cohort_registry cohorts;
    survival_needs_registry needs;
    survival_consumption_scheduler consumption;
    survival_production_action_registry actions;
    survival_production_scheduler production;

    life_body_registry bodies;
    life_person_registry persons;
    life_person_account_registry person_accounts;
    life_account_owner_registry account_owners;
    life_death_event_list death_events;
    life_estate_registry estates;
    life_inheritance_action_list inheritance_actions;
    life_inheritance_scheduler inheritance_scheduler;
    life_audit_log audit_log;
    life_controller_binding_set bindings;
    life_post_death_rights_registry rights;
    life_remains_registry remains;
    life_remains_decay_scheduler remains_decay;
    life_remains_aggregate_registry remains_aggregates;
    dom_ledger ledger;
    life_death_context death_ctx;

    dom_mp0_cohort_binding cohort_bindings[DOM_MP0_MAX_COHORTS];
    u32 cohort_binding_count;

    survival_cohort cohorts_storage[DOM_MP0_MAX_COHORTS];
    survival_needs_entry needs_storage[DOM_MP0_MAX_COHORTS];
    dom_time_event consumption_events[DOM_MP0_MAX_COHORTS * 4u];
    dg_due_entry consumption_entries[DOM_MP0_MAX_COHORTS];
    survival_consumption_due_user consumption_users[DOM_MP0_MAX_COHORTS];

    survival_production_action actions_storage[DOM_MP0_MAX_ACTIONS];
    dom_time_event production_events[DOM_MP0_MAX_ACTIONS * 2u];
    dg_due_entry production_entries[DOM_MP0_MAX_ACTIONS];
    survival_production_due_user production_users[DOM_MP0_MAX_ACTIONS];

    life_body_record bodies_storage[DOM_MP0_MAX_PERSONS];
    life_person_record persons_storage[DOM_MP0_MAX_PERSONS];
    life_death_event death_events_storage[DOM_MP0_MAX_DEATH_EVENTS];
    life_estate estates_storage[DOM_MP0_MAX_ESTATES];
    dom_account_id_t estate_account_storage[DOM_MP0_MAX_ACCOUNTS];
    life_person_account_entry person_account_entries[DOM_MP0_MAX_PERSONS];
    dom_account_id_t person_account_storage[DOM_MP0_MAX_ACCOUNTS];
    life_account_owner_entry owner_storage[DOM_MP0_MAX_ACCOUNTS];
    life_inheritance_action inheritance_storage[DOM_MP0_MAX_INHERIT_ACTIONS];
    dom_time_event inheritance_events[DOM_MP0_MAX_INHERIT_ACTIONS * 2u];
    dg_due_entry inheritance_entries[DOM_MP0_MAX_INHERIT_ACTIONS];
    life_inheritance_due_user inheritance_users[DOM_MP0_MAX_INHERIT_ACTIONS];
    life_audit_entry audit_storage[DOM_MP0_MAX_INHERIT_ACTIONS * 2u];
    life_controller_binding bindings_storage[DOM_MP0_MAX_PERSONS];

    life_post_death_rights rights_storage[DOM_MP0_MAX_RIGHTS];
    life_remains remains_storage[DOM_MP0_MAX_REMAINS];
    life_remains_aggregate remains_aggregate_storage[DOM_MP0_MAX_REMAINS];
    dom_time_event remains_events[DOM_MP0_MAX_REMAINS * 2u];
    dg_due_entry remains_entries[DOM_MP0_MAX_REMAINS];
    life_remains_decay_user remains_users[DOM_MP0_MAX_REMAINS];
} dom_mp0_state;

void dom_mp0_command_queue_init(dom_mp0_command_queue* queue,
                                dom_mp0_command* storage,
                                u32 capacity);
int dom_mp0_command_add_production(dom_mp0_command_queue* queue,
                                   dom_act_time_t tick,
                                   const survival_production_action_input* input);
int dom_mp0_command_add_continuation(dom_mp0_command_queue* queue,
                                     dom_act_time_t tick,
                                     const life_cmd_continuation_select* cmd);
void dom_mp0_command_sort(dom_mp0_command_queue* queue);

int dom_mp0_state_init(dom_mp0_state* state, dom_act_time_t start_tick);
int dom_mp0_register_cohort(dom_mp0_state* state,
                            u64 cohort_id,
                            u32 count,
                            u64 location_ref,
                            u64 person_id,
                            u64 body_id,
                            dom_account_id_t account_id);
int dom_mp0_set_needs(dom_mp0_state* state,
                      u64 cohort_id,
                      u32 food,
                      u32 water,
                      u32 shelter);
int dom_mp0_bind_controller(dom_mp0_state* state,
                            u64 controller_id,
                            u64 person_id);

int dom_mp0_run(dom_mp0_state* state,
                const dom_mp0_command_queue* queue,
                dom_act_time_t target_tick);

u64 dom_mp0_hash_state(const dom_mp0_state* state);
void dom_mp0_copy_authoritative(const dom_mp0_state* src, dom_mp0_state* dst);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SESSION_MP0_SESSION_H */
