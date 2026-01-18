/*
FILE: game/rules/knowledge/knowledge_item.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / knowledge
RESPONSIBILITY: Implements knowledge items and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Knowledge ordering and updates are deterministic.
*/
#include "dominium/rules/knowledge/knowledge_item.h"

#include <string.h>

static u32 knowledge_clamp_completeness(u32 value)
{
    if (value > KNOWLEDGE_COMPLETENESS_MAX) {
        return KNOWLEDGE_COMPLETENESS_MAX;
    }
    return value;
}

void knowledge_registry_init(knowledge_registry* reg,
                             knowledge_item* storage,
                             u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->items = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(knowledge_item) * (size_t)capacity);
    }
}

static u32 knowledge_find_index(const knowledge_registry* reg,
                                u64 knowledge_id,
                                int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->items) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->items[i].knowledge_id == knowledge_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->items[i].knowledge_id > knowledge_id) {
            break;
        }
    }
    return i;
}

int knowledge_register(knowledge_registry* reg,
                       u64 knowledge_id,
                       knowledge_type type,
                       u32 domain_tags)
{
    int found = 0;
    u32 idx;
    u32 i;
    knowledge_item* entry;
    if (!reg || !reg->items) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = knowledge_find_index(reg, knowledge_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->items[i] = reg->items[i - 1u];
    }
    entry = &reg->items[idx];
    memset(entry, 0, sizeof(*entry));
    entry->knowledge_id = knowledge_id;
    entry->type = type;
    entry->domain_tags = domain_tags;
    entry->completeness = 0u;
    entry->provenance_ref = 0u;
    entry->status = KNOW_STATUS_UNKNOWN;
    reg->count += 1u;
    return 0;
}

knowledge_item* knowledge_find(knowledge_registry* reg, u64 knowledge_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->items) {
        return 0;
    }
    idx = knowledge_find_index(reg, knowledge_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->items[idx];
}

int knowledge_set_completeness(knowledge_registry* reg,
                               u64 knowledge_id,
                               u32 completeness)
{
    knowledge_item* item = knowledge_find(reg, knowledge_id);
    if (!item) {
        return -1;
    }
    item->completeness = knowledge_clamp_completeness(completeness);
    if (item->completeness >= KNOWLEDGE_COMPLETENESS_MAX) {
        item->status = KNOW_STATUS_KNOWN;
    }
    return 0;
}

int knowledge_add_completeness(knowledge_registry* reg,
                               u64 knowledge_id,
                               u32 delta)
{
    knowledge_item* item = knowledge_find(reg, knowledge_id);
    u32 value;
    if (!item) {
        return -1;
    }
    value = item->completeness + delta;
    item->completeness = knowledge_clamp_completeness(value);
    if (item->completeness >= KNOWLEDGE_COMPLETENESS_MAX) {
        item->status = KNOW_STATUS_KNOWN;
    }
    return 0;
}

int knowledge_set_status(knowledge_registry* reg,
                         u64 knowledge_id,
                         knowledge_epistemic_status status)
{
    knowledge_item* item = knowledge_find(reg, knowledge_id);
    if (!item) {
        return -1;
    }
    item->status = status;
    return 0;
}
