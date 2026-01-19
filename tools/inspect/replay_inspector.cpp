/*
FILE: tools/inspect/replay_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Implements deterministic replay inspection utilities.
ALLOWED DEPENDENCIES: Engine public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Uses deterministic hashing and ordering.
*/
#include "replay_inspector.h"

#include <stddef.h>

static u64 tool_replay_hash_bytes(u64 hash, const unsigned char* bytes, size_t len) {
    size_t i;
    for (i = 0u; i < len; ++i) {
        hash ^= (u64)bytes[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

u64 tool_replay_hash(const tool_replay* replay) {
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!replay || !replay->events || replay->event_count == 0u) {
        return 0u;
    }
    for (i = 0u; i < replay->event_count; ++i) {
        const tool_replay_event* ev = &replay->events[i];
        hash = tool_replay_hash_bytes(hash,
                                      (const unsigned char*)&ev->event_id,
                                      sizeof(ev->event_id));
        hash = tool_replay_hash_bytes(hash,
                                      (const unsigned char*)&ev->act,
                                      sizeof(ev->act));
        hash = tool_replay_hash_bytes(hash,
                                      (const unsigned char*)&ev->kind,
                                      sizeof(ev->kind));
        hash = tool_replay_hash_bytes(hash,
                                      (const unsigned char*)&ev->required_knowledge,
                                      sizeof(ev->required_knowledge));
        hash = tool_replay_hash_bytes(hash,
                                      (const unsigned char*)&ev->flags,
                                      sizeof(ev->flags));
    }
    return hash;
}

int tool_replay_inspector_init(tool_replay_inspector* insp,
                               const tool_replay* replay,
                               const tool_access_context* access) {
    if (!insp || !replay) {
        return TOOL_INSPECT_INVALID;
    }
    insp->replay = replay;
    insp->cursor = 0u;
    if (access) {
        insp->access = *access;
    } else {
        insp->access.mode = TOOL_ACCESS_EPISTEMIC;
        insp->access.knowledge_mask = 0u;
    }
    return TOOL_INSPECT_OK;
}

int tool_replay_inspector_seek(tool_replay_inspector* insp, dom_act_time_t act) {
    u32 i;
    if (!insp || !insp->replay) {
        return TOOL_INSPECT_INVALID;
    }
    insp->cursor = insp->replay->event_count;
    for (i = 0u; i < insp->replay->event_count; ++i) {
        if (insp->replay->events[i].act >= act) {
            insp->cursor = i;
            break;
        }
    }
    return TOOL_INSPECT_OK;
}

int tool_replay_inspector_next(tool_replay_inspector* insp,
                               tool_replay_view_event* out_event) {
    if (!insp || !insp->replay || !out_event) {
        return TOOL_INSPECT_INVALID;
    }
    while (insp->cursor < insp->replay->event_count) {
        const tool_replay_event* ev = &insp->replay->events[insp->cursor++];
        if (!tool_inspect_access_allows(&insp->access, ev->required_knowledge)) {
            continue;
        }
        out_event->event_id = ev->event_id;
        out_event->act = ev->act;
        out_event->kind = ev->kind;
        out_event->flags = ev->flags;
        out_event->visible = 1u;
        return TOOL_INSPECT_OK;
    }
    return TOOL_INSPECT_NO_DATA;
}
