/*
FILE: tools/inspect/event_timeline_view.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Implements deterministic event timeline inspection utilities.
ALLOWED DEPENDENCIES: Engine public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and filtering.
*/
#include "event_timeline_view.h"

static int tool_event_is_visible(const tool_access_context* access,
                                 const tool_event_record* ev) {
    if (!ev) {
        return 0;
    }
    return tool_inspect_access_allows(access, ev->required_knowledge);
}

static int tool_event_less(const tool_event_record* a, const tool_event_record* b) {
    if (a->act < b->act) {
        return 1;
    }
    if (a->act > b->act) {
        return 0;
    }
    return (a->event_id < b->event_id) ? 1 : 0;
}

int tool_event_timeline_next_due(const tool_event_timeline* timeline,
                                 const tool_access_context* access,
                                 dom_act_time_t now_act,
                                 dom_act_time_t* out_next_act) {
    u32 i;
    int found = 0;
    dom_act_time_t best = 0;
    if (!timeline || !out_next_act) {
        return TOOL_INSPECT_INVALID;
    }
    for (i = 0u; i < timeline->event_count; ++i) {
        const tool_event_record* ev = &timeline->events[i];
        if (ev->state != TOOL_EVENT_PENDING) {
            continue;
        }
        if (!tool_event_is_visible(access, ev)) {
            continue;
        }
        if (ev->act < now_act) {
            continue;
        }
        if (!found || ev->act < best) {
            best = ev->act;
            found = 1;
        }
    }
    if (!found) {
        return TOOL_INSPECT_NO_DATA;
    }
    *out_next_act = best;
    return TOOL_INSPECT_OK;
}

int tool_event_timeline_collect(const tool_event_timeline* timeline,
                                const tool_access_context* access,
                                dom_act_time_t start_act,
                                dom_act_time_t end_act,
                                tool_event_record* out_events,
                                u32 max_events,
                                u32* out_count) {
    u32 i;
    u32 count = 0u;
    if (!timeline || !out_events || !out_count) {
        return TOOL_INSPECT_INVALID;
    }
    for (i = 0u; i < timeline->event_count; ++i) {
        const tool_event_record* ev = &timeline->events[i];
        u32 insert_pos;
        u32 j;
        if (ev->act < start_act || ev->act > end_act) {
            continue;
        }
        if (!tool_event_is_visible(access, ev)) {
            continue;
        }
        if (count >= max_events) {
            return TOOL_INSPECT_INVALID;
        }
        insert_pos = count;
        for (j = 0u; j < count; ++j) {
            if (tool_event_less(ev, &out_events[j])) {
                insert_pos = j;
                break;
            }
        }
        for (j = count; j > insert_pos; --j) {
            out_events[j] = out_events[j - 1u];
        }
        out_events[insert_pos] = *ev;
        count += 1u;
    }
    *out_count = count;
    return TOOL_INSPECT_OK;
}
