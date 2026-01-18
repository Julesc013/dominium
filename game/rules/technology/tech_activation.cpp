/*
FILE: game/rules/technology/tech_activation.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / technology
RESPONSIBILITY: Implements deterministic technology activation rules.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Activation checks are deterministic.
*/
#include "dominium/rules/technology/tech_activation.h"

#include <string.h>

void tech_activation_registry_init(tech_activation_registry* reg,
                                   tech_activation* storage,
                                   u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->activations = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(tech_activation) * (size_t)capacity);
    }
}

static u32 tech_activation_find_index(const tech_activation_registry* reg,
                                      u64 tech_id,
                                      u64 actor_id,
                                      int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->activations) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        const tech_activation* entry = &reg->activations[i];
        if (entry->tech_id == tech_id && entry->actor_id == actor_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (entry->tech_id > tech_id ||
            (entry->tech_id == tech_id && entry->actor_id > actor_id)) {
            break;
        }
    }
    return i;
}

int tech_activation_request(tech_activation_registry* reg,
                            const tech_prereq_registry* prereqs,
                            const knowledge_registry* knowledge,
                            u64 tech_id,
                            u64 actor_id,
                            dom_act_time_t act,
                            int acknowledged)
{
    int found = 0;
    u32 idx;
    u32 i;
    tech_activation* entry;
    if (!reg || !reg->activations || !prereqs || !knowledge) {
        return -1;
    }
    if (!acknowledged) {
        return -2;
    }
    if (!tech_prereqs_met(prereqs, knowledge, tech_id)) {
        return -3;
    }
    idx = tech_activation_find_index(reg, tech_id, actor_id, &found);
    if (!found) {
        if (reg->count >= reg->capacity) {
            return -4;
        }
        for (i = reg->count; i > idx; --i) {
            reg->activations[i] = reg->activations[i - 1u];
        }
        entry = &reg->activations[idx];
        memset(entry, 0, sizeof(*entry));
        entry->tech_id = tech_id;
        entry->actor_id = actor_id;
        reg->count += 1u;
    } else {
        entry = &reg->activations[idx];
    }
    entry->status = TECH_ACTIVE;
    entry->activated_act = act;
    return 0;
}

int tech_activation_is_active(const tech_activation_registry* reg,
                              u64 tech_id,
                              u64 actor_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->activations) {
        return 0;
    }
    idx = tech_activation_find_index(reg, tech_id, actor_id, &found);
    if (!found) {
        return 0;
    }
    return reg->activations[idx].status == TECH_ACTIVE;
}
