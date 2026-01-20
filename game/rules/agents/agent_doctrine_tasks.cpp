/*
FILE: game/rules/agents/agent_doctrine_tasks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements doctrine and role update helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Doctrine updates are deterministic.
*/
#include "dominium/rules/agents/agent_doctrine_tasks.h"

#include <string.h>

void dom_agent_role_buffer_init(dom_agent_role_buffer* buffer,
                                dom_agent_role_state* storage,
                                u32 capacity)
{
    if (!buffer) {
        return;
    }
    buffer->entries = storage;
    buffer->count = 0u;
    buffer->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_agent_role_state) * (size_t)capacity);
    }
}

void dom_agent_role_buffer_reset(dom_agent_role_buffer* buffer)
{
    if (!buffer) {
        return;
    }
    buffer->count = 0u;
}

static u32 dom_agent_role_find_index(const dom_agent_role_buffer* buffer,
                                     u64 agent_id,
                                     int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!buffer || !buffer->entries) {
        return 0u;
    }
    for (i = 0u; i < buffer->count; ++i) {
        if (buffer->entries[i].agent_id == agent_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (buffer->entries[i].agent_id > agent_id) {
            break;
        }
    }
    return i;
}

int dom_agent_role_buffer_set(dom_agent_role_buffer* buffer,
                              const dom_agent_role_state* state)
{
    int found = 0;
    u32 idx;
    u32 i;
    dom_agent_role_state* entry;
    if (!buffer || !buffer->entries || !state) {
        return -1;
    }
    idx = dom_agent_role_find_index(buffer, state->agent_id, &found);
    if (found) {
        buffer->entries[idx] = *state;
        return 0;
    }
    if (buffer->count >= buffer->capacity) {
        return -2;
    }
    for (i = buffer->count; i > idx; --i) {
        buffer->entries[i] = buffer->entries[i - 1u];
    }
    entry = &buffer->entries[idx];
    *entry = *state;
    buffer->count += 1u;
    return 0;
}

u32 dom_agent_apply_doctrine_slice(const dom_agent_doctrine_entry* doctrines,
                                   u32 doctrine_count,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_agent_role_buffer* roles,
                                   dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!doctrines || !roles || start_index >= doctrine_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > doctrine_count) {
        end = doctrine_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_role_state state;
        state.agent_id = doctrines[i].agent_id;
        state.role_id = doctrines[i].role_id;
        state.allowed_action_mask = doctrines[i].allowed_action_mask;
        if (dom_agent_role_buffer_set(roles, &state) == 0 && audit) {
            dom_agent_audit_record(audit, DOM_AGENT_AUDIT_DOCTRINE_APPLY,
                                   state.agent_id, (i64)state.role_id);
        }
    }
    return end - start_index;
}

u32 dom_agent_update_roles_slice(dom_agent_role_buffer* roles,
                                 u32 start_index,
                                 u32 max_count,
                                 dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!roles || !roles->entries || start_index >= roles->count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > roles->count) {
        end = roles->count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_role_state* state = &roles->entries[i];
        if (audit) {
            dom_agent_audit_record(audit, DOM_AGENT_AUDIT_ROLE_UPDATE,
                                   state->agent_id, (i64)state->role_id);
        }
    }
    return end - start_index;
}
