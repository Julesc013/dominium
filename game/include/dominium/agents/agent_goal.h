/*
FILE: include/dominium/agents/agent_goal.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines agent goals, preconditions, refusal codes, and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Goal ordering and feasibility checks are deterministic.
*/
#ifndef DOMINIUM_AGENTS_AGENT_GOAL_H
#define DOMINIUM_AGENTS_AGENT_GOAL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define AGENT_PRIORITY_SCALE 1000u
#define AGENT_NEED_SCALE 1000u

typedef enum agent_goal_type {
    AGENT_GOAL_SURVIVE = 0,
    AGENT_GOAL_ACQUIRE = 1,
    AGENT_GOAL_DEFEND = 2,
    AGENT_GOAL_MIGRATE = 3,
    AGENT_GOAL_RESEARCH = 4,
    AGENT_GOAL_TRADE = 5
} agent_goal_type;

#define AGENT_GOAL_TYPE_COUNT 6u

typedef enum agent_refusal_code {
    AGENT_REFUSAL_NONE = 0,
    AGENT_REFUSAL_GOAL_NOT_FEASIBLE = 1,
    AGENT_REFUSAL_INSUFFICIENT_CAPABILITY = 2,
    AGENT_REFUSAL_INSUFFICIENT_AUTHORITY = 3,
    AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE = 4,
    AGENT_REFUSAL_PLAN_EXPIRED = 5,
    AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED = 6,
    AGENT_REFUSAL_GOAL_FORBIDDEN_BY_DOCTRINE = 7,
    AGENT_REFUSAL_DELEGATION_EXPIRED = 8,
    AGENT_REFUSAL_ROLE_MISMATCH = 9
} agent_refusal_code;

enum {
    AGENT_CAP_MOVE = 1u << 0,
    AGENT_CAP_TRADE = 1u << 1,
    AGENT_CAP_DEFEND = 1u << 2,
    AGENT_CAP_RESEARCH = 1u << 3
};

enum {
    AGENT_AUTH_BASIC = 1u << 0,
    AGENT_AUTH_TRADE = 1u << 1,
    AGENT_AUTH_MILITARY = 1u << 2
};

enum {
    AGENT_KNOW_RESOURCE = 1u << 0,
    AGENT_KNOW_SAFE_ROUTE = 1u << 1,
    AGENT_KNOW_THREAT = 1u << 2
};

typedef struct agent_goal_preconditions {
    u32 required_capabilities;
    u32 required_authority;
    u32 required_knowledge;
} agent_goal_preconditions;

typedef struct agent_goal {
    u64 goal_id;
    u32 type;
    u32 base_priority;
    agent_goal_preconditions preconditions;
    u32 satisfaction_flags;
    dom_act_time_t expiry_act;
} agent_goal;

typedef struct agent_goal_registry {
    agent_goal* goals;
    u32 count;
    u32 capacity;
    u64 next_goal_id;
} agent_goal_registry;

void agent_goal_registry_init(agent_goal_registry* reg,
                              agent_goal* storage,
                              u32 capacity,
                              u64 start_goal_id);
agent_goal* agent_goal_find(agent_goal_registry* reg,
                            u64 goal_id);
int agent_goal_register(agent_goal_registry* reg,
                        u64 goal_id,
                        u32 type,
                        u32 base_priority,
                        const agent_goal_preconditions* preconditions,
                        u32 satisfaction_flags,
                        dom_act_time_t expiry_act);

const char* agent_refusal_to_string(agent_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_GOAL_H */
