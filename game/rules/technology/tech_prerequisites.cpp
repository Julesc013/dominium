/*
FILE: game/rules/technology/tech_prerequisites.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / technology
RESPONSIBILITY: Implements technology prerequisites based on knowledge thresholds.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Prerequisite ordering and checks are deterministic.
*/
#include "dominium/rules/technology/tech_prerequisites.h"

#include <string.h>

void tech_prereq_registry_init(tech_prereq_registry* reg,
                               tech_prerequisite* storage,
                               u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->prereqs = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(tech_prerequisite) * (size_t)capacity);
    }
}

static u32 tech_prereq_find_index(const tech_prereq_registry* reg,
                                  u64 tech_id,
                                  u64 knowledge_id,
                                  int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->prereqs) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        const tech_prerequisite* entry = &reg->prereqs[i];
        if (entry->tech_id == tech_id && entry->knowledge_id == knowledge_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (entry->tech_id > tech_id ||
            (entry->tech_id == tech_id && entry->knowledge_id > knowledge_id)) {
            break;
        }
    }
    return i;
}

int tech_prereq_register(tech_prereq_registry* reg,
                         u64 tech_id,
                         u64 knowledge_id,
                         u32 min_completeness)
{
    int found = 0;
    u32 idx;
    u32 i;
    tech_prerequisite* entry;
    if (!reg || !reg->prereqs) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = tech_prereq_find_index(reg, tech_id, knowledge_id, &found);
    if (found) {
        reg->prereqs[idx].min_completeness = min_completeness;
        return 0;
    }
    for (i = reg->count; i > idx; --i) {
        reg->prereqs[i] = reg->prereqs[i - 1u];
    }
    entry = &reg->prereqs[idx];
    entry->tech_id = tech_id;
    entry->knowledge_id = knowledge_id;
    entry->min_completeness = min_completeness;
    reg->count += 1u;
    return 0;
}

int tech_prereqs_met(const tech_prereq_registry* reg,
                     const knowledge_registry* knowledge,
                     u64 tech_id)
{
    u32 i;
    int found_any = 0;
    if (!reg || !knowledge) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        const tech_prerequisite* req = &reg->prereqs[i];
        const knowledge_item* item;
        if (req->tech_id != tech_id) {
            continue;
        }
        found_any = 1;
        item = knowledge_find((knowledge_registry*)knowledge, req->knowledge_id);
        if (!item || item->completeness < req->min_completeness) {
            return 0;
        }
    }
    if (!found_any) {
        return 1;
    }
    return 1;
}
