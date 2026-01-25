/*
FILE: tools/observability/observation_store.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Defines immutable observation store records for read-only tools.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Store iteration order is deterministic for identical inputs.
*/
#ifndef DOMINIUM_TOOLS_OBSERVATION_STORE_H
#define DOMINIUM_TOOLS_OBSERVATION_STORE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    TOOL_OBSERVE_OK = 0,
    TOOL_OBSERVE_NO_DATA = -1,
    TOOL_OBSERVE_REFUSED = -2,
    TOOL_OBSERVE_INVALID = -3
};

enum {
    TOOL_WORLD_VALUE_UNKNOWN = 1u << 0,
    TOOL_WORLD_VALUE_LATENT = 1u << 1
};

enum {
    TOOL_EVENT_FLAG_FAILED = 1u << 0,
    TOOL_EVENT_FLAG_PARTIAL = 1u << 1,
    TOOL_EVENT_FLAG_SIDE_EFFECT = 1u << 2
};

enum {
    TOOL_PACK_FLAG_ENABLED = 1u << 0,
    TOOL_PACK_FLAG_OVERRIDE = 1u << 1,
    TOOL_PACK_FLAG_DISABLED = 1u << 2,
    TOOL_PACK_FLAG_MISSING_DEP = 1u << 3
};

enum {
    TOOL_HISTORY_FLAG_CONFLICT = 1u << 0,
    TOOL_HISTORY_FLAG_PROPAGANDA = 1u << 1,
    TOOL_HISTORY_FLAG_REDACTED = 1u << 2,
    TOOL_HISTORY_FLAG_INCOMPLETE = 1u << 3
};

enum {
    TOOL_AGENT_GOAL_ACTIVE = 1u,
    TOOL_AGENT_GOAL_DEFERRED = 2u,
    TOOL_AGENT_GOAL_ABANDONED = 3u
};

enum {
    TOOL_PLAN_STEP_PENDING = 0u,
    TOOL_PLAN_STEP_COMPLETED = 1u,
    TOOL_PLAN_STEP_FAILED = 2u
};

enum {
    TOOL_CONTRACT_ACTIVE = 1u,
    TOOL_CONTRACT_FULFILLED = 2u,
    TOOL_CONTRACT_BREACHED = 3u
};

enum {
    TOOL_DELEGATION_ACTIVE = 1u,
    TOOL_DELEGATION_REVOKED = 2u
};

enum {
    TOOL_CONSTRAINT_ACTIVE = 1u,
    TOOL_CONSTRAINT_SUSPENDED = 2u
};

enum {
    TOOL_ENFORCEMENT_PERMIT = 1u,
    TOOL_ENFORCEMENT_DENY = 2u,
    TOOL_ENFORCEMENT_PENALIZE = 3u,
    TOOL_ENFORCEMENT_REWARD = 4u
};

enum {
    TOOL_INSTITUTION_COLLAPSE_FRAGMENT = 1u,
    TOOL_INSTITUTION_COLLAPSE_DISSOLVE = 2u,
    TOOL_INSTITUTION_COLLAPSE_OVERTHROWN = 3u
};

typedef struct tool_snapshot_record {
    u64 snapshot_id;
    u64 schema_id;
    u32 schema_version;
    u32 kind; /* dom_snapshot_kind */
    u32 lod_tag;
    u32 budget_units;
    u32 scope_mask;
    u32 knowledge_mask;
    const void* payload;
    u32 payload_size;
} tool_snapshot_record;

typedef struct tool_observe_event_record {
    u64 event_id;
    dom_act_time_t act;
    u64 agent_id;
    u64 institution_id;
    u64 process_id;
    u32 kind;
    u32 required_knowledge;
    u32 authority_mask;
    u32 flags;
    u64 belief_id;
    u64 constraint_id;
    i64 amount;
    i32 outcome_code;
    u32 reserved;
} tool_observe_event_record;

typedef struct tool_history_record {
    u64 history_id;
    dom_act_time_t act;
    u64 agent_id;
    u64 institution_id;
    u64 provenance_id;
    u32 kind;
    u32 flags;
    u32 required_knowledge;
    u32 reserved;
    i64 amount;
} tool_history_record;

typedef struct tool_pack_record {
    u64 pack_id;
    u32 precedence;
    u32 flags;
} tool_pack_record;

typedef struct tool_capability_record {
    u64 capability_id;
    u64 pack_id;
    u32 provider_kind;
    u32 flags;
} tool_capability_record;

typedef struct tool_agent_state {
    u64 agent_id;
    u32 capability_mask;
    u32 authority_mask;
    u32 knowledge_mask;
    u32 goal_count;
    u32 failure_count;
    u32 belief_count;
    u32 memory_count;
    u32 plan_count;
} tool_agent_state;

typedef struct tool_institution_state {
    u64 institution_id;
    u32 authority_mask;
    u32 knowledge_mask;
    u32 legitimacy_q16;
    u32 status;
    u32 constraint_count;
    u32 contract_count;
    u32 delegation_count;
    u32 enforcement_count;
    u32 collapse_count;
} tool_institution_state;

typedef struct tool_world_cell {
    u32 x;
    u32 y;
    u32 field_id;
    i32 value_q16;
    u32 flags;
} tool_world_cell;

typedef struct tool_topology_node {
    u64 node_id;
    u64 parent_id;
} tool_topology_node;

typedef struct tool_observe_replay_event {
    u64 event_id;
    dom_act_time_t act;
    u32 kind;
    u32 flags;
    u64 agent_id;
} tool_observe_replay_event;

typedef struct tool_observe_replay {
    const tool_observe_replay_event* events;
    u32 event_count;
} tool_observe_replay;

typedef struct tool_agent_goal_record {
    u64 goal_id;
    u64 agent_id;
    u64 condition_id;
    u32 priority_q16;
    u32 urgency_q16;
    u32 risk_q16;
    dom_act_time_t horizon_act;
    u32 confidence_q16;
    u32 status;
    u32 required_knowledge;
} tool_agent_goal_record;

typedef struct tool_agent_belief_record {
    u64 belief_id;
    u64 agent_id;
    u64 knowledge_id;
    dom_act_time_t observed_act;
    u32 confidence_q16;
    u32 flags;
    u32 required_knowledge;
    u32 reserved;
} tool_agent_belief_record;

typedef struct tool_agent_memory_record {
    u64 memory_id;
    u64 agent_id;
    u32 kind;
    u32 strength_q16;
    u32 decay_q16;
    dom_act_time_t last_act;
    u32 required_knowledge;
} tool_agent_memory_record;

typedef struct tool_agent_plan_step_record {
    u64 plan_id;
    u64 agent_id;
    u64 process_id;
    u32 step_index;
    u32 status;
    u32 required_capability;
    u32 expected_cost_q16;
    u32 confidence_q16;
    u32 required_knowledge;
    u32 failure_flags;
} tool_agent_plan_step_record;

typedef struct tool_agent_failure_record {
    u64 failure_id;
    u64 agent_id;
    u64 process_id;
    dom_act_time_t act;
    u32 failure_kind;
    u32 required_knowledge;
} tool_agent_failure_record;

typedef struct tool_contract_record {
    u64 contract_id;
    u64 institution_id;
    u64 agent_a;
    u64 agent_b;
    dom_act_time_t act;
    u32 status;
    u32 flags;
    u32 required_knowledge;
    u32 reserved;
} tool_contract_record;

typedef struct tool_delegation_record {
    u64 delegation_id;
    u64 from_agent_id;
    u64 to_agent_id;
    u64 institution_id;
    dom_act_time_t act;
    u32 authority_mask;
    u32 status;
    u32 required_knowledge;
    u32 reserved;
} tool_delegation_record;

typedef struct tool_constraint_record {
    u64 constraint_id;
    u64 institution_id;
    u32 kind;
    u32 status;
    u32 required_knowledge;
    u32 reserved;
} tool_constraint_record;

typedef struct tool_enforcement_record {
    u64 enforcement_id;
    u64 institution_id;
    u64 agent_id;
    u64 process_id;
    dom_act_time_t act;
    u32 kind;
    u32 status;
    u32 required_knowledge;
    u32 reserved;
} tool_enforcement_record;

typedef struct tool_institution_collapse_record {
    u64 collapse_id;
    u64 institution_id;
    dom_act_time_t act;
    u32 kind;
    u32 required_knowledge;
    u32 reserved;
} tool_institution_collapse_record;

typedef struct tool_observation_store_desc {
    const tool_snapshot_record* snapshots;
    u32 snapshot_count;
    const tool_observe_event_record* events;
    u32 event_count;
    const tool_history_record* history;
    u32 history_count;
    const tool_pack_record* packs;
    u32 pack_count;
    const tool_capability_record* capabilities;
    u32 capability_count;
    const tool_agent_state* agents;
    u32 agent_count;
    const tool_agent_goal_record* agent_goals;
    u32 agent_goal_count;
    const tool_agent_belief_record* agent_beliefs;
    u32 agent_belief_count;
    const tool_agent_memory_record* agent_memory;
    u32 agent_memory_count;
    const tool_agent_plan_step_record* agent_plan_steps;
    u32 agent_plan_step_count;
    const tool_agent_failure_record* agent_failures;
    u32 agent_failure_count;
    const tool_institution_state* institutions;
    u32 institution_count;
    const tool_contract_record* contracts;
    u32 contract_count;
    const tool_delegation_record* delegations;
    u32 delegation_count;
    const tool_constraint_record* constraints;
    u32 constraint_count;
    const tool_enforcement_record* enforcement;
    u32 enforcement_count;
    const tool_institution_collapse_record* collapses;
    u32 collapse_count;
    const tool_world_cell* world_cells;
    u32 world_cell_count;
    const tool_topology_node* topology;
    u32 topology_count;
    const tool_observe_replay* replay;
} tool_observation_store_desc;

typedef tool_observation_store_desc tool_observation_store;

void tool_observation_store_init(tool_observation_store* store,
                                 const tool_observation_store_desc* desc);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVATION_STORE_H */
