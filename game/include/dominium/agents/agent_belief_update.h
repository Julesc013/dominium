/*
FILE: include/dominium/agents/agent_belief_update.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines deterministic agent belief updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Belief updates are event-driven and ordered by ACT time.
*/
#ifndef DOMINIUM_AGENTS_AGENT_BELIEF_UPDATE_H
#define DOMINIUM_AGENTS_AGENT_BELIEF_UPDATE_H

#include "dominium/agents/agent_goal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum agent_belief_flags {
    AGENT_BELIEF_FLAG_NONE = 0u,
    AGENT_BELIEF_FLAG_HEARSAY = (1u << 0u),
    AGENT_BELIEF_FLAG_DISTORTED = (1u << 1u)
} agent_belief_flags;

typedef enum agent_belief_topic {
    AGENT_BELIEF_TOPIC_RESOURCE = 1u,
    AGENT_BELIEF_TOPIC_SAFE_ROUTE = 2u,
    AGENT_BELIEF_TOPIC_THREAT = 3u,
    AGENT_BELIEF_TOPIC_GOAL_HINT = 4u
} agent_belief_topic;

typedef enum agent_belief_event_kind {
    AGENT_BELIEF_EVENT_OBSERVE = 1u,
    AGENT_BELIEF_EVENT_MEASURE = 2u,
    AGENT_BELIEF_EVENT_INFER = 3u,
    AGENT_BELIEF_EVENT_HEAR = 4u,
    AGENT_BELIEF_EVENT_FORGET = 5u,
    AGENT_BELIEF_EVENT_DISTORT = 6u
} agent_belief_event_kind;

typedef struct agent_belief_entry {
    u64 belief_id;
    u64 agent_id;
    u64 knowledge_ref;
    u32 topic_id;
    u32 confidence_q16;
    dom_act_time_t observed_act;
    dom_act_time_t expires_act;
    u32 flags;
} agent_belief_entry;

typedef struct agent_belief_store {
    agent_belief_entry* entries;
    u32 count;
    u32 capacity;
    u64 next_id;
    u32 decay_q16_per_act;
    u32 min_confidence_q16;
    dom_act_time_t last_decay_act;
} agent_belief_store;

typedef struct agent_belief_event {
    u64 agent_id;
    u64 knowledge_ref;
    u32 topic_id;
    u32 kind;
    u32 confidence_q16;
    i32 confidence_delta_q16;
    dom_act_time_t observed_act;
    dom_act_time_t expires_act;
    u32 flags_set;
    u32 flags_clear;
} agent_belief_event;

typedef struct agent_belief_state {
    u64 agent_id;
    u32 knowledge_mask;
    u32 hunger_level;
    u32 threat_level;
    dom_act_time_t last_update_act;
} agent_belief_state;

typedef struct agent_observation_event {
    u32 knowledge_grant_mask;
    u32 knowledge_clear_mask;
    i32 hunger_delta;
    i32 threat_delta;
} agent_observation_event;

typedef struct agent_command_outcome {
    u32 command_type;
    int success;
    agent_refusal_code refusal;
    u32 knowledge_clear_mask;
    i32 hunger_delta;
    i32 threat_delta;
} agent_command_outcome;

void agent_belief_store_init(agent_belief_store* store,
                             agent_belief_entry* storage,
                             u32 capacity,
                             u64 start_id,
                             u32 decay_q16_per_act,
                             u32 min_confidence_q16);
int agent_belief_store_apply_event(agent_belief_store* store,
                                   const agent_belief_event* event,
                                   dom_act_time_t now_act);
void agent_belief_store_decay(agent_belief_store* store,
                              dom_act_time_t now_act);
const agent_belief_entry* agent_belief_store_best_topic(const agent_belief_store* store,
                                                        u64 agent_id,
                                                        u32 topic_id);
u32 agent_belief_store_mask(const agent_belief_store* store,
                            u64 agent_id);

void agent_belief_init(agent_belief_state* state,
                       u64 agent_id,
                       u32 knowledge_mask,
                       u32 hunger_level,
                       u32 threat_level,
                       dom_act_time_t now_act);
int agent_belief_apply_observation(agent_belief_state* state,
                                   const agent_observation_event* obs,
                                   dom_act_time_t now_act);
int agent_belief_apply_command_outcome(agent_belief_state* state,
                                       const agent_command_outcome* outcome,
                                       dom_act_time_t now_act);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_BELIEF_UPDATE_H */
