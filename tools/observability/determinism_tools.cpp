/*
FILE: tools/observability/determinism_tools.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements determinism and regression comparison helpers.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic hashing and comparison.
*/
#include "determinism_tools.h"

#include <string.h>

static u64 tool_det_hash_bytes(u64 hash, const unsigned char* bytes, u32 len)
{
    u32 i;
    for (i = 0u; i < len; ++i) {
        hash ^= (u64)bytes[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

u64 tool_determinism_hash_events(const tool_observe_event_record* events,
                                 u32 event_count)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!events || event_count == 0u) {
        return 0u;
    }
    for (i = 0u; i < event_count; ++i) {
        hash = tool_det_hash_bytes(hash,
                                   (const unsigned char*)&events[i],
                                   (u32)sizeof(tool_observe_event_record));
    }
    return hash;
}

u64 tool_determinism_hash_snapshots(const tool_snapshot_record* snapshots,
                                    u32 snapshot_count)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!snapshots || snapshot_count == 0u) {
        return 0u;
    }
    for (i = 0u; i < snapshot_count; ++i) {
        hash = tool_det_hash_bytes(hash,
                                   (const unsigned char*)&snapshots[i].snapshot_id,
                                   (u32)sizeof(snapshots[i].snapshot_id));
        hash = tool_det_hash_bytes(hash,
                                   (const unsigned char*)&snapshots[i].schema_id,
                                   (u32)sizeof(snapshots[i].schema_id));
        hash = tool_det_hash_bytes(hash,
                                   (const unsigned char*)&snapshots[i].schema_version,
                                   (u32)sizeof(snapshots[i].schema_version));
        hash = tool_det_hash_bytes(hash,
                                   (const unsigned char*)&snapshots[i].kind,
                                   (u32)sizeof(snapshots[i].kind));
    }
    return hash;
}

int tool_determinism_compare_replays(const tool_observe_replay* left,
                                     const tool_observe_replay* right,
                                     tool_determinism_diff* out_diff)
{
    u32 i;
    if (!out_diff) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_diff, 0, sizeof(*out_diff));
    if (!left || !right || !left->events || !right->events) {
        return TOOL_OBSERVE_NO_DATA;
    }
    if (left->event_count != right->event_count) {
        out_diff->diverged = 1u;
        out_diff->kind = TOOL_DET_DIFF_COUNT;
        out_diff->left_id = left->event_count;
        out_diff->right_id = right->event_count;
        return TOOL_OBSERVE_OK;
    }
    for (i = 0u; i < left->event_count; ++i) {
        const tool_observe_replay_event* a = &left->events[i];
        const tool_observe_replay_event* b = &right->events[i];
        if (a->event_id != b->event_id) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_EVENT_ID;
            out_diff->left_id = a->event_id;
            out_diff->right_id = b->event_id;
            return TOOL_OBSERVE_OK;
        }
        if (a->act != b->act) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_EVENT_ACT;
            out_diff->left_id = (u64)a->act;
            out_diff->right_id = (u64)b->act;
            return TOOL_OBSERVE_OK;
        }
        if (a->kind != b->kind) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_EVENT_KIND;
            out_diff->left_id = a->kind;
            out_diff->right_id = b->kind;
            return TOOL_OBSERVE_OK;
        }
        if (a->flags != b->flags) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_EVENT_FLAGS;
            out_diff->left_id = a->flags;
            out_diff->right_id = b->flags;
            return TOOL_OBSERVE_OK;
        }
        if (a->agent_id != b->agent_id) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_EVENT_AGENT;
            out_diff->left_id = a->agent_id;
            out_diff->right_id = b->agent_id;
            return TOOL_OBSERVE_OK;
        }
    }
    return TOOL_OBSERVE_OK;
}

int tool_determinism_compare_events(const tool_observe_event_record* left,
                                    u32 left_count,
                                    const tool_observe_event_record* right,
                                    u32 right_count,
                                    tool_determinism_diff* out_diff)
{
    u32 i;
    if (!out_diff) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_diff, 0, sizeof(*out_diff));
    if (!left || !right) {
        return TOOL_OBSERVE_NO_DATA;
    }
    if (left_count != right_count) {
        out_diff->diverged = 1u;
        out_diff->kind = TOOL_DET_DIFF_COUNT;
        out_diff->left_id = left_count;
        out_diff->right_id = right_count;
        return TOOL_OBSERVE_OK;
    }
    for (i = 0u; i < left_count; ++i) {
        if (memcmp(&left[i], &right[i], sizeof(tool_observe_event_record)) != 0) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_EVENT_ID;
            out_diff->left_id = left[i].event_id;
            out_diff->right_id = right[i].event_id;
            return TOOL_OBSERVE_OK;
        }
    }
    return TOOL_OBSERVE_OK;
}

int tool_determinism_compare_snapshots(const tool_snapshot_record* left,
                                       u32 left_count,
                                       const tool_snapshot_record* right,
                                       u32 right_count,
                                       tool_determinism_diff* out_diff)
{
    u32 i;
    if (!out_diff) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(out_diff, 0, sizeof(*out_diff));
    if (!left || !right) {
        return TOOL_OBSERVE_NO_DATA;
    }
    if (left_count != right_count) {
        out_diff->diverged = 1u;
        out_diff->kind = TOOL_DET_DIFF_COUNT;
        out_diff->left_id = left_count;
        out_diff->right_id = right_count;
        return TOOL_OBSERVE_OK;
    }
    for (i = 0u; i < left_count; ++i) {
        const tool_snapshot_record* a = &left[i];
        const tool_snapshot_record* b = &right[i];
        if (a->snapshot_id != b->snapshot_id ||
            a->schema_id != b->schema_id ||
            a->schema_version != b->schema_version ||
            a->kind != b->kind) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_SNAPSHOT_META;
            out_diff->left_id = a->snapshot_id;
            out_diff->right_id = b->snapshot_id;
            return TOOL_OBSERVE_OK;
        }
        if (a->payload_size != b->payload_size) {
            out_diff->diverged = 1u;
            out_diff->index = i;
            out_diff->kind = TOOL_DET_DIFF_SNAPSHOT_PAYLOAD;
            out_diff->left_id = a->payload_size;
            out_diff->right_id = b->payload_size;
            return TOOL_OBSERVE_OK;
        }
        if (a->payload && b->payload && a->payload_size != 0u) {
            if (memcmp(a->payload, b->payload, a->payload_size) != 0) {
                out_diff->diverged = 1u;
                out_diff->index = i;
                out_diff->kind = TOOL_DET_DIFF_SNAPSHOT_PAYLOAD;
                out_diff->left_id = a->snapshot_id;
                out_diff->right_id = b->snapshot_id;
                return TOOL_OBSERVE_OK;
            }
        }
    }
    return TOOL_OBSERVE_OK;
}
