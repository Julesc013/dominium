/*
FILE: game/rules/knowledge/institution_knowledge_binding.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / knowledge
RESPONSIBILITY: Implements knowledge-holding institutions and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Institution ordering and holdings are deterministic.
*/
#include "dominium/rules/knowledge/institution_knowledge_binding.h"

#include <string.h>

void knowledge_institution_registry_init(knowledge_institution_registry* reg,
                                         knowledge_institution* storage,
                                         u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->institutions = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(knowledge_institution) * (size_t)capacity);
    }
}

static u32 knowledge_institution_find_index(const knowledge_institution_registry* reg,
                                            u64 institution_id,
                                            int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->institutions) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->institutions[i].institution_id == institution_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->institutions[i].institution_id > institution_id) {
            break;
        }
    }
    return i;
}

int knowledge_institution_register(knowledge_institution_registry* reg,
                                   u64 institution_id,
                                   knowledge_institution_type type,
                                   u32 capacity,
                                   u64 secrecy_policy_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    knowledge_institution* entry;
    if (!reg || !reg->institutions) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = knowledge_institution_find_index(reg, institution_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->institutions[i] = reg->institutions[i - 1u];
    }
    entry = &reg->institutions[idx];
    memset(entry, 0, sizeof(*entry));
    entry->institution_id = institution_id;
    entry->type = type;
    entry->capacity = capacity;
    entry->secrecy_policy_id = secrecy_policy_id;
    entry->holdings_count = 0u;
    reg->count += 1u;
    return 0;
}

knowledge_institution* knowledge_institution_find(knowledge_institution_registry* reg,
                                                  u64 institution_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->institutions) {
        return 0;
    }
    idx = knowledge_institution_find_index(reg, institution_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->institutions[idx];
}

static int knowledge_institution_insert_holding(knowledge_institution* inst,
                                                u64 knowledge_id)
{
    u32 i;
    if (!inst) {
        return -1;
    }
    if (inst->holdings_count >= KNOWLEDGE_MAX_HOLDINGS) {
        return -2;
    }
    for (i = 0u; i < inst->holdings_count; ++i) {
        if (inst->holdings[i] == knowledge_id) {
            return 0;
        }
        if (inst->holdings[i] > knowledge_id) {
            break;
        }
    }
    if (i < inst->holdings_count) {
        u32 j;
        for (j = inst->holdings_count; j > i; --j) {
            inst->holdings[j] = inst->holdings[j - 1u];
        }
    }
    inst->holdings[i] = knowledge_id;
    inst->holdings_count += 1u;
    return 0;
}

int knowledge_institution_add_holding(knowledge_institution_registry* reg,
                                      u64 institution_id,
                                      u64 knowledge_id)
{
    knowledge_institution* inst = knowledge_institution_find(reg, institution_id);
    if (!inst) {
        return -1;
    }
    return knowledge_institution_insert_holding(inst, knowledge_id);
}

int knowledge_institution_knows(const knowledge_institution_registry* reg,
                                u64 institution_id,
                                u64 knowledge_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->institutions) {
        return 0;
    }
    idx = knowledge_institution_find_index(reg, institution_id, &found);
    if (!found) {
        return 0;
    }
    for (i = 0u; i < reg->institutions[idx].holdings_count; ++i) {
        if (reg->institutions[idx].holdings[i] == knowledge_id) {
            return 1;
        }
    }
    return 0;
}
