/*
FILE: tools/observability/agent_inspector.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Read-only inspection of agent state, goals, beliefs, plans, and failures.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and iteration.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_AGENT_INSPECTOR_H
#define DOMINIUM_TOOLS_OBSERVABILITY_AGENT_INSPECTOR_H

#include "domino/core/types.h"
#include "inspect_access.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_agent_inspector {
    const tool_observation_store* store;
    tool_access_context access;
    u64 agent_id;
    u32 goal_cursor;
    u32 belief_cursor;
    u32 memory_cursor;
    u32 plan_cursor;
    u32 failure_cursor;
} tool_agent_inspector;

int tool_agent_inspector_init(tool_agent_inspector* insp,
                              const tool_observation_store* store,
                              const tool_access_context* access,
                              u64 agent_id);
int tool_agent_inspector_reset(tool_agent_inspector* insp);
int tool_agent_inspector_state(const tool_agent_inspector* insp,
                               tool_agent_state* out_state);
int tool_agent_inspector_next_goal(tool_agent_inspector* insp,
                                   tool_agent_goal_record* out_goal);
int tool_agent_inspector_next_belief(tool_agent_inspector* insp,
                                     tool_agent_belief_record* out_belief);
int tool_agent_inspector_next_memory(tool_agent_inspector* insp,
                                     tool_agent_memory_record* out_memory);
int tool_agent_inspector_next_plan_step(tool_agent_inspector* insp,
                                        tool_agent_plan_step_record* out_step);
int tool_agent_inspector_next_failure(tool_agent_inspector* insp,
                                      tool_agent_failure_record* out_failure);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_AGENT_INSPECTOR_H */
