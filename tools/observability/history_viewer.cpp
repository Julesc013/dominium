/*
FILE: tools/observability/history_viewer.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements history browsing, provenance tracing, and causal lookup.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and ordering.
*/
#include "history_viewer.h"

#include <string.h>

static void tool_history_access_default(tool_access_context* access)
{
    if (!access) {
        return;
    }
    access->mode = TOOL_ACCESS_EPISTEMIC;
    access->knowledge_mask = 0u;
}

int tool_history_viewer_init(tool_history_viewer* viewer,
                             const tool_observation_store* store,
                             const tool_access_context* access,
                             u64 agent_id,
                             u64 institution_id,
                             u32 flags_mask)
{
    if (!viewer || !store) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(viewer, 0, sizeof(*viewer));
    viewer->store = store;
    viewer->agent_id = agent_id;
    viewer->institution_id = institution_id;
    viewer->flags_mask = flags_mask;
    if (access) {
        viewer->access = *access;
    } else {
        tool_history_access_default(&viewer->access);
    }
    return TOOL_OBSERVE_OK;
}

int tool_history_viewer_next(tool_history_viewer* viewer,
                             tool_history_record* out_record)
{
    if (!viewer || !out_record || !viewer->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!viewer->store->history || viewer->store->history_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (viewer->cursor < viewer->store->history_count) {
        const tool_history_record* rec = &viewer->store->history[viewer->cursor++];
        if (viewer->agent_id != 0u && rec->agent_id != viewer->agent_id) {
            continue;
        }
        if (viewer->institution_id != 0u && rec->institution_id != viewer->institution_id) {
            continue;
        }
        if (viewer->flags_mask != 0u && (rec->flags & viewer->flags_mask) == 0u) {
            continue;
        }
        if (!tool_inspect_access_allows(&viewer->access, rec->required_knowledge)) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_history_viewer_collect_range(const tool_observation_store* store,
                                      const tool_access_context* access,
                                      dom_act_time_t start_act,
                                      dom_act_time_t end_act,
                                      tool_history_record* out_records,
                                      u32 max_records,
                                      u32* out_count)
{
    tool_access_context local_access;
    const tool_access_context* ctx = access;
    u32 count = 0u;
    u32 i;
    if (!store || !out_records || !out_count) {
        return TOOL_OBSERVE_INVALID;
    }
    *out_count = 0u;
    if (!ctx) {
        tool_history_access_default(&local_access);
        ctx = &local_access;
    }
    if (!store->history || store->history_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < store->history_count; ++i) {
        const tool_history_record* rec = &store->history[i];
        if (rec->act < start_act || rec->act > end_act) {
            continue;
        }
        if (!tool_inspect_access_allows(ctx, rec->required_knowledge)) {
            continue;
        }
        if (count < max_records) {
            out_records[count] = *rec;
        }
        count += 1u;
    }
    *out_count = count;
    return (count == 0u) ? TOOL_OBSERVE_NO_DATA : TOOL_OBSERVE_OK;
}

int tool_history_viewer_trace_provenance(const tool_observation_store* store,
                                         const tool_access_context* access,
                                         u64 provenance_id,
                                         tool_history_record* out_records,
                                         u32 max_records,
                                         u32* out_count)
{
    tool_access_context local_access;
    const tool_access_context* ctx = access;
    u32 count = 0u;
    u32 i;
    if (!store || !out_records || !out_count) {
        return TOOL_OBSERVE_INVALID;
    }
    *out_count = 0u;
    if (!ctx) {
        tool_history_access_default(&local_access);
        ctx = &local_access;
    }
    if (!store->history || store->history_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < store->history_count; ++i) {
        const tool_history_record* rec = &store->history[i];
        if (provenance_id != 0u && rec->provenance_id != provenance_id) {
            continue;
        }
        if (!tool_inspect_access_allows(ctx, rec->required_knowledge)) {
            continue;
        }
        if (count < max_records) {
            out_records[count] = *rec;
        }
        count += 1u;
    }
    *out_count = count;
    return (count == 0u) ? TOOL_OBSERVE_NO_DATA : TOOL_OBSERVE_OK;
}

int tool_history_viewer_explain_event(const tool_observation_store* store,
                                      const tool_access_context* access,
                                      u64 event_id,
                                      tool_history_explanation* out_explanation)
{
    tool_access_context local_access;
    const tool_access_context* ctx = access;
    u32 i;
    if (!store || !out_explanation) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_explanation, 0, sizeof(*out_explanation));
    if (!ctx) {
        tool_history_access_default(&local_access);
        ctx = &local_access;
    }
    if (!store->events || store->event_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < store->event_count; ++i) {
        const tool_observe_event_record* ev = &store->events[i];
        if (event_id != 0u && ev->event_id != event_id) {
            continue;
        }
        if (!tool_inspect_access_allows(ctx, ev->required_knowledge)) {
            return TOOL_OBSERVE_REFUSED;
        }
        out_explanation->event = *ev;
        out_explanation->has_event = 1u;
        break;
    }
    if (out_explanation->has_event == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    if (store->agents && store->agent_count != 0u) {
        for (i = 0u; i < store->agent_count; ++i) {
            const tool_agent_state* agent = &store->agents[i];
            if (agent->agent_id != out_explanation->event.agent_id) {
                continue;
            }
            if (!tool_inspect_access_allows(ctx, agent->knowledge_mask)) {
                break;
            }
            out_explanation->agent = *agent;
            out_explanation->has_agent = 1u;
            break;
        }
    }
    if (store->institutions && store->institution_count != 0u &&
        out_explanation->event.institution_id != 0u) {
        for (i = 0u; i < store->institution_count; ++i) {
            const tool_institution_state* inst = &store->institutions[i];
            if (inst->institution_id != out_explanation->event.institution_id) {
                continue;
            }
            if (!tool_inspect_access_allows(ctx, inst->knowledge_mask)) {
                break;
            }
            out_explanation->institution = *inst;
            out_explanation->has_institution = 1u;
            break;
        }
    }
    return TOOL_OBSERVE_OK;
}
