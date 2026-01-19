/*
FILE: include/dominium/agents/doctrine.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines doctrine policy data and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Doctrine selection and filtering are deterministic.
*/
#ifndef DOMINIUM_AGENTS_DOCTRINE_H
#define DOMINIUM_AGENTS_DOCTRINE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/agents/agent_goal.h"

#ifdef __cplusplus
extern "C" {
#endif

#define AGENT_GOAL_BIT(type) (1u << (type))

typedef enum agent_doctrine_scope {
    DOCTRINE_SCOPE_AGENT = 0,
    DOCTRINE_SCOPE_COHORT = 1,
    DOCTRINE_SCOPE_ORG = 2,
    DOCTRINE_SCOPE_JURISDICTION = 3
} agent_doctrine_scope;

typedef enum agent_doctrine_sched_policy {
    DOCTRINE_SCHED_ANY = 0,
    DOCTRINE_SCHED_INTERVAL = 1,
    DOCTRINE_SCHED_WINDOW = 2
} agent_doctrine_sched_policy;

typedef struct agent_doctrine {
    u64 doctrine_id;
    u64 owner_ref;
    u32 scope;
    u32 allowed_goal_types;
    u32 forbidden_goal_types;
    i32 priority_modifiers[AGENT_GOAL_TYPE_COUNT];
    u32 scheduling_policy;
    dom_act_time_t min_think_interval_act;
    dom_act_time_t window_start_act;
    dom_act_time_t window_end_act;
    dom_act_time_t expiry_act;
    u32 authority_required_mask;
    u32 legitimacy_min;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
} agent_doctrine;

typedef struct agent_doctrine_registry {
    agent_doctrine* doctrines;
    u32 count;
    u32 capacity;
} agent_doctrine_registry;

typedef struct agent_doctrine_binding {
    u64 explicit_doctrine_ref;
    u64 role_doctrine_ref;
    u64 org_doctrine_ref;
    u64 jurisdiction_doctrine_ref;
    u64 personal_doctrine_ref;
    u32 authority_mask;
    u32 legitimacy_value;
} agent_doctrine_binding;

void agent_doctrine_registry_init(agent_doctrine_registry* reg,
                                  agent_doctrine* storage,
                                  u32 capacity);
agent_doctrine* agent_doctrine_find(agent_doctrine_registry* reg,
                                    u64 doctrine_id);
int agent_doctrine_register(agent_doctrine_registry* reg,
                            const agent_doctrine* doctrine);
int agent_doctrine_update(agent_doctrine_registry* reg,
                          const agent_doctrine* doctrine);
int agent_doctrine_remove(agent_doctrine_registry* reg,
                          u64 doctrine_id);

int agent_doctrine_is_authorized(const agent_doctrine* doctrine,
                                 const agent_doctrine_binding* binding,
                                 agent_refusal_code* out_refusal);
int agent_doctrine_allows_goal(const agent_doctrine* doctrine,
                               u32 goal_type);
u32 agent_doctrine_apply_priority(const agent_doctrine* doctrine,
                                  u32 goal_type,
                                  u32 base_priority);
dom_act_time_t agent_doctrine_next_think_act(const agent_doctrine* doctrine,
                                             dom_act_time_t last_act,
                                             dom_act_time_t desired_act);
const agent_doctrine* agent_doctrine_select(const agent_doctrine_registry* reg,
                                            const agent_doctrine_binding* binding,
                                            dom_act_time_t now_act,
                                            agent_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_DOCTRINE_H */
