/*
FILE: include/dominium/player.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / player
RESPONSIBILITY: Defines player embodiment as first-class agent intent and feedback APIs.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Intent validation and event ordering are deterministic.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**` without cross-layer coupling.
*/
#ifndef DOMINIUM_PLAYER_H
#define DOMINIUM_PLAYER_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "dominium/agents/agent_goal.h"
#include "dominium/rules/agents/agent_planning_tasks.h"
#include "dominium/agents/agent_authority.h"
#include "dominium/physical/field_storage.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dom_player_id;

typedef enum dom_player_refusal_code {
    DOM_PLAYER_REFUSAL_NONE = 0,
    DOM_PLAYER_REFUSAL_NO_CAPABILITY = 1,
    DOM_PLAYER_REFUSAL_NO_AUTHORITY = 2,
    DOM_PLAYER_REFUSAL_NO_KNOWLEDGE = 3,
    DOM_PLAYER_REFUSAL_PHYSICAL_CONSTRAINT = 4,
    DOM_PLAYER_REFUSAL_INVALID_INTENT = 5,
    DOM_PLAYER_REFUSAL_PLAN_NOT_FOUND = 6
} dom_player_refusal_code;

typedef enum dom_player_intent_kind {
    DOM_PLAYER_INTENT_GOAL_UPDATE = 1,
    DOM_PLAYER_INTENT_PLAN_CONFIRM = 2,
    DOM_PLAYER_INTENT_PROCESS_REQUEST = 3
} dom_player_intent_kind;

typedef enum dom_player_intent_status {
    DOM_PLAYER_INTENT_PENDING = 0,
    DOM_PLAYER_INTENT_ACCEPTED = 1,
    DOM_PLAYER_INTENT_REFUSED = 2
} dom_player_intent_status;

typedef enum dom_player_event_kind {
    DOM_PLAYER_EVENT_INTENT_ACCEPTED = 1,
    DOM_PLAYER_EVENT_INTENT_REFUSED = 2,
    DOM_PLAYER_EVENT_INTENT_RECORDED = 3
} dom_player_event_kind;

typedef struct dom_player_record {
    dom_player_id player_id;
    u64 agent_id;
    u32 flags;
} dom_player_record;

typedef struct dom_player_registry {
    dom_player_record* entries;
    u32 count;
    u32 capacity;
} dom_player_registry;

typedef struct dom_player_goal_update {
    agent_goal_desc desc;
} dom_player_goal_update;

typedef struct dom_player_process_request {
    u32 process_kind;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 required_knowledge_mask;
    u32 x;
    u32 y;
    i32 max_slope_q16;
    i32 min_bearing_q16;
    u64 target_id;
} dom_player_process_request;

typedef struct dom_player_intent {
    u64 intent_id;
    dom_player_id player_id;
    u64 agent_id;
    u32 kind;
    u32 status;
    u32 refusal;
    dom_act_time_t submitted_act;
    union {
        dom_player_goal_update goal_update;
        dom_player_process_request process_request;
        u64 plan_id;
    } payload;
} dom_player_intent;

typedef struct dom_player_intent_queue {
    dom_player_intent* entries;
    u32 count;
    u32 capacity;
    u64 next_intent_id;
} dom_player_intent_queue;

typedef struct dom_player_event {
    u64 event_id;
    dom_player_id player_id;
    u64 agent_id;
    u32 kind;
    u64 intent_id;
    u32 refusal;
    dom_act_time_t act_time;
} dom_player_event;

typedef struct dom_player_event_log {
    dom_player_event* entries;
    u32 count;
    u32 capacity;
    u64 next_event_id;
} dom_player_event_log;

typedef struct dom_player_subjective_snapshot {
    u64 agent_id;
    u32 knowledge_mask;
    u32 epistemic_confidence_q16;
    u64 known_resource_ref;
    u64 known_threat_ref;
    u64 known_destination_ref;
} dom_player_subjective_snapshot;

void dom_player_registry_init(dom_player_registry* registry,
                              dom_player_record* storage,
                              u32 capacity);
dom_player_record* dom_player_find(dom_player_registry* registry,
                                   dom_player_id player_id);
int dom_player_bind(dom_player_registry* registry,
                    dom_player_id player_id,
                    u64 agent_id);

void dom_player_intent_queue_init(dom_player_intent_queue* queue,
                                  dom_player_intent* storage,
                                  u32 capacity,
                                  u64 start_id);
void dom_player_event_log_init(dom_player_event_log* log,
                               dom_player_event* storage,
                               u32 capacity,
                               u64 start_id);
int dom_player_event_record(dom_player_event_log* log,
                            dom_player_id player_id,
                            u64 agent_id,
                            u32 kind,
                            u64 intent_id,
                            u32 refusal,
                            dom_act_time_t act_time);

int dom_player_build_snapshot(const dom_agent_belief* beliefs,
                              u32 belief_count,
                              u64 agent_id,
                              dom_player_subjective_snapshot* out_snapshot);

typedef struct dom_player_intent_context {
    const dom_agent_capability* caps;
    u32 cap_count;
    const dom_agent_belief* beliefs;
    u32 belief_count;
    const agent_authority_registry* authority;
    dom_field_storage* fields;
    dom_act_time_t now_act;
    dom_player_event_log* events;
    agent_goal_registry* goals;
} dom_player_intent_context;

int dom_player_submit_intent(dom_player_intent_queue* queue,
                             const dom_player_intent* intent,
                             const dom_player_intent_context* ctx);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_PLAYER_H */
