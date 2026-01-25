/*
FILE: include/dominium/agents/agent_history_macro.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines macro-history aggregation from audit events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: History aggregation is ordered by source event id.
*/
#ifndef DOMINIUM_AGENTS_AGENT_HISTORY_MACRO_H
#define DOMINIUM_AGENTS_AGENT_HISTORY_MACRO_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/agents/agent_planning_tasks.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum agent_history_flags {
    AGENT_HISTORY_FLAG_NONE = 0u,
    AGENT_HISTORY_FLAG_PROPAGANDA = (1u << 0u),
    AGENT_HISTORY_FLAG_LOST = (1u << 1u)
} agent_history_flags;

typedef struct agent_history_record {
    u64 history_id;
    u64 source_event_id;
    u64 narrative_id;
    u64 agent_id;
    u64 institution_id;
    u64 subject_id;
    dom_act_time_t act_time;
    u32 kind;
    u32 flags;
    i64 amount;
} agent_history_record;

typedef struct agent_history_buffer {
    agent_history_record* entries;
    u32 count;
    u32 capacity;
    u64 next_id;
} agent_history_buffer;

typedef struct agent_history_policy {
    const u64* narrative_ids;
    u32 narrative_count;
    u32 include_objective;
} agent_history_policy;

void agent_history_buffer_init(agent_history_buffer* buffer,
                               agent_history_record* storage,
                               u32 capacity,
                               u64 start_id);
void agent_history_buffer_reset(agent_history_buffer* buffer);

u32 agent_history_aggregate(const dom_agent_audit_log* audit,
                            const agent_history_policy* policy,
                            agent_history_buffer* out_history);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_HISTORY_MACRO_H */
