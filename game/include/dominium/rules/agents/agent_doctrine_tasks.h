/*
FILE: include/dominium/rules/agents/agent_doctrine_tasks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Work IR task helpers for doctrine and role updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Doctrine updates are deterministic.
*/
#ifndef DOMINIUM_RULES_AGENTS_AGENT_DOCTRINE_TASKS_H
#define DOMINIUM_RULES_AGENTS_AGENT_DOCTRINE_TASKS_H

#include "dominium/rules/agents/agent_planning_tasks.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_agent_doctrine_entry {
    u64 agent_id;
    u32 doctrine_id;
    u32 role_id;
    u32 allowed_action_mask;
} dom_agent_doctrine_entry;

typedef struct dom_agent_role_state {
    u64 agent_id;
    u32 role_id;
    u32 allowed_action_mask;
} dom_agent_role_state;

typedef struct dom_agent_role_buffer {
    dom_agent_role_state* entries;
    u32 count;
    u32 capacity;
} dom_agent_role_buffer;

void dom_agent_role_buffer_init(dom_agent_role_buffer* buffer,
                                dom_agent_role_state* storage,
                                u32 capacity);
void dom_agent_role_buffer_reset(dom_agent_role_buffer* buffer);
int dom_agent_role_buffer_set(dom_agent_role_buffer* buffer,
                              const dom_agent_role_state* state);

u32 dom_agent_apply_doctrine_slice(const dom_agent_doctrine_entry* doctrines,
                                   u32 doctrine_count,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_agent_role_buffer* roles,
                                   dom_agent_audit_log* audit);

u32 dom_agent_update_roles_slice(dom_agent_role_buffer* roles,
                                 u32 start_index,
                                 u32 max_count,
                                 dom_agent_audit_log* audit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_AGENTS_AGENT_DOCTRINE_TASKS_H */
