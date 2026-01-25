/*
FILE: game/agents/agent_institution.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements institution registries and collapse checks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Institutions are ordered by institution_id.
*/
#include "dominium/agents/agent_institution.h"

#include <string.h>

void agent_institution_registry_init(agent_institution_registry* reg,
                                     agent_institution* storage,
                                     u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_institution) * (size_t)capacity);
    }
}

static u32 agent_institution_find_index(const agent_institution_registry* reg,
                                        u64 institution_id,
                                        int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->entries) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].institution_id == institution_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->entries[i].institution_id > institution_id) {
            break;
        }
    }
    return i;
}

agent_institution* agent_institution_find(agent_institution_registry* reg,
                                          u64 institution_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->entries) {
        return 0;
    }
    idx = agent_institution_find_index(reg, institution_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->entries[idx];
}

int agent_institution_register(agent_institution_registry* reg,
                               u64 institution_id,
                               u64 agent_id,
                               u32 authority_mask,
                               u32 legitimacy_q16,
                               dom_act_time_t founded_act,
                               dom_provenance_id provenance_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_institution* entry;
    if (!reg || !reg->entries || institution_id == 0u || agent_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_institution_find_index(reg, institution_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->entries[i] = reg->entries[i - 1u];
    }
    entry = &reg->entries[idx];
    memset(entry, 0, sizeof(*entry));
    entry->institution_id = institution_id;
    entry->agent_id = agent_id;
    entry->authority_mask = authority_mask;
    entry->legitimacy_q16 = legitimacy_q16;
    entry->status = AGENT_INSTITUTION_ACTIVE;
    entry->founded_act = founded_act;
    entry->collapsed_act = 0u;
    entry->provenance_id = provenance_id ? provenance_id : institution_id;
    entry->flags = 0u;
    reg->count += 1u;
    return 0;
}

int agent_institution_set_legitimacy(agent_institution* inst,
                                     u32 legitimacy_q16)
{
    if (!inst) {
        return -1;
    }
    inst->legitimacy_q16 = legitimacy_q16;
    return 0;
}

int agent_institution_check_collapse(agent_institution* inst,
                                     u32 collapse_threshold_q16,
                                     dom_act_time_t now_act)
{
    if (!inst) {
        return -1;
    }
    if (inst->status == AGENT_INSTITUTION_COLLAPSED) {
        return 0;
    }
    if (inst->legitimacy_q16 <= collapse_threshold_q16) {
        inst->status = AGENT_INSTITUTION_COLLAPSED;
        inst->collapsed_act = now_act;
        return 1;
    }
    return 0;
}
