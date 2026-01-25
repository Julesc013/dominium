/*
FILE: tools/observability/observability_api.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements read-only tool interfaces for snapshots, events, history, replay, packs, and capabilities.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: All queries are deterministic and side-effect free.
*/
#include "observability_api.h"

#include <string.h>

static void tool_access_default(tool_access_context* access)
{
    if (!access) {
        return;
    }
    access->mode = TOOL_ACCESS_EPISTEMIC;
    access->knowledge_mask = 0u;
}

static int tool_access_allows_objective(const tool_access_context* access)
{
    if (!access) {
        return 0;
    }
    return (access->mode == TOOL_ACCESS_PRIVILEGED) ? 1 : 0;
}

int tool_snapshot_query(const tool_observation_store* store,
                        const tool_snapshot_request* request,
                        const tool_access_context* access,
                        tool_snapshot_view* out_view)
{
    tool_access_context local_access;
    const tool_access_context* ctx = access;
    int refused = 0;
    u32 i;
    if (!store || !request || !out_view) {
        return TOOL_OBSERVE_INVALID;
    }
    if (request->lod_tag == 0u || request->budget_units == 0u) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!ctx) {
        tool_access_default(&local_access);
        ctx = &local_access;
    }
    if (request->kind_set != 0u &&
        request->kind == DOM_SNAPSHOT_OBJECTIVE &&
        !tool_access_allows_objective(ctx)) {
        return TOOL_OBSERVE_REFUSED;
    }
    if (!store->snapshots || store->snapshot_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < store->snapshot_count; ++i) {
        const tool_snapshot_record* rec = &store->snapshots[i];
        if (request->snapshot_id != 0u && rec->snapshot_id != request->snapshot_id) {
            continue;
        }
        if (request->kind_set != 0u && rec->kind != request->kind) {
            continue;
        }
        if (rec->kind == DOM_SNAPSHOT_OBJECTIVE && !tool_access_allows_objective(ctx)) {
            refused = 1;
            continue;
        }
        if (rec->lod_tag != request->lod_tag) {
            continue;
        }
        if (rec->budget_units > request->budget_units) {
            refused = 1;
            continue;
        }
        if (request->scope_mask != 0u && (rec->scope_mask & request->scope_mask) == 0u) {
            continue;
        }
        if (!tool_inspect_access_allows(ctx, rec->knowledge_mask)) {
            refused = 1;
            continue;
        }
        out_view->record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return refused ? TOOL_OBSERVE_REFUSED : TOOL_OBSERVE_NO_DATA;
}

int tool_event_stream_subscribe(const tool_observation_store* store,
                                const tool_event_stream_request* request,
                                const tool_access_context* access,
                                tool_event_stream* out_stream)
{
    if (!store || !out_stream) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_stream, 0, sizeof(*out_stream));
    out_stream->store = store;
    if (request) {
        out_stream->request = *request;
    }
    if (access) {
        out_stream->access = *access;
    } else {
        tool_access_default(&out_stream->access);
    }
    if (!store->events || store->event_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    return TOOL_OBSERVE_OK;
}

int tool_event_stream_next(tool_event_stream* stream,
                           tool_observe_event_record* out_event)
{
    if (!stream || !out_event || !stream->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!stream->store->events || stream->store->event_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (stream->cursor < stream->store->event_count) {
        const tool_observe_event_record* ev = &stream->store->events[stream->cursor++];
        if (stream->request.agent_id != 0u && ev->agent_id != stream->request.agent_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&stream->access, ev->required_knowledge)) {
            continue;
        }
        if (stream->request.required_knowledge != 0u &&
            (ev->required_knowledge & stream->request.required_knowledge) == 0u) {
            continue;
        }
        *out_event = *ev;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_history_query(const tool_observation_store* store,
                       const tool_history_query* request,
                       const tool_access_context* access,
                       tool_history_view* out_view)
{
    if (!store || !out_view) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_view, 0, sizeof(*out_view));
    out_view->store = store;
    if (request) {
        out_view->request = *request;
    }
    if (access) {
        out_view->access = *access;
    } else {
        tool_access_default(&out_view->access);
    }
    if (!store->history || store->history_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    return TOOL_OBSERVE_OK;
}

int tool_history_view_next(tool_history_view* view,
                           tool_history_record* out_record)
{
    if (!view || !out_record || !view->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!view->store->history || view->store->history_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (view->cursor < view->store->history_count) {
        const tool_history_record* rec = &view->store->history[view->cursor++];
        if (view->request.agent_id != 0u && rec->agent_id != view->request.agent_id) {
            continue;
        }
        if (view->request.institution_id != 0u &&
            rec->institution_id != view->request.institution_id) {
            continue;
        }
        if (view->request.flags_mask != 0u &&
            (rec->flags & view->request.flags_mask) == 0u) {
            continue;
        }
        if (!tool_inspect_access_allows(&view->access, rec->required_knowledge)) {
            continue;
        }
        if (view->request.required_knowledge != 0u &&
            (rec->required_knowledge & view->request.required_knowledge) == 0u) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_replay_control(tool_replay_controller* controller,
                        const tool_replay_command* command,
                        tool_replay_state* out_state)
{
    if (!controller || !command || !out_state) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_state, 0, sizeof(*out_state));
    switch (command->kind) {
        case TOOL_REPLAY_CMD_LOAD:
            controller->replay = command->replay;
            controller->cursor = 0u;
            break;
        case TOOL_REPLAY_CMD_RESET:
            controller->cursor = 0u;
            break;
        case TOOL_REPLAY_CMD_SEEK:
            if (!controller->replay || !controller->replay->events) {
                return TOOL_OBSERVE_NO_DATA;
            }
            controller->cursor = 0u;
            while (controller->cursor < controller->replay->event_count &&
                   controller->replay->events[controller->cursor].act < command->act) {
                controller->cursor += 1u;
            }
            break;
        case TOOL_REPLAY_CMD_STEP:
            if (!controller->replay || !controller->replay->events) {
                return TOOL_OBSERVE_NO_DATA;
            }
            if (controller->cursor >= controller->replay->event_count) {
                return TOOL_OBSERVE_NO_DATA;
            }
            out_state->current = controller->replay->events[controller->cursor];
            out_state->has_current = 1u;
            controller->cursor += 1u;
            break;
        default:
            return TOOL_OBSERVE_INVALID;
    }
    out_state->cursor = controller->cursor;
    return TOOL_OBSERVE_OK;
}

int tool_pack_manifest_query(const tool_observation_store* store,
                             const tool_pack_query* request,
                             tool_pack_view* out_view)
{
    if (!store || !out_view) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_view, 0, sizeof(*out_view));
    out_view->store = store;
    if (request) {
        out_view->request = *request;
    }
    if (!store->packs || store->pack_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    return TOOL_OBSERVE_OK;
}

int tool_pack_view_next(tool_pack_view* view,
                        tool_pack_record* out_record)
{
    if (!view || !out_record || !view->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!view->store->packs || view->store->pack_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (view->cursor < view->store->pack_count) {
        const tool_pack_record* rec = &view->store->packs[view->cursor++];
        if (view->request.include_disabled == 0u &&
            (rec->flags & TOOL_PACK_FLAG_DISABLED) != 0u) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_capability_query(const tool_observation_store* store,
                          const tool_capability_query* request,
                          tool_capability_view* out_view)
{
    if (!store || !out_view) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_view, 0, sizeof(*out_view));
    out_view->store = store;
    if (request) {
        out_view->request = *request;
    }
    if (!store->capabilities || store->capability_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    return TOOL_OBSERVE_OK;
}

int tool_capability_view_next(tool_capability_view* view,
                              tool_capability_record* out_record)
{
    if (!view || !out_record || !view->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!view->store->capabilities || view->store->capability_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (view->cursor < view->store->capability_count) {
        const tool_capability_record* rec = &view->store->capabilities[view->cursor++];
        if (view->request.provider_kind != 0u &&
            rec->provider_kind != view->request.provider_kind) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}
