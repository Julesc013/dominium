/*
FILE: game/agents/agent_contract.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements agent contract registries and checks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Contracts are evaluated in stable order.
*/
#include "dominium/agents/agent_contract.h"

#include <string.h>

void agent_contract_registry_init(agent_contract_registry* reg,
                                  agent_contract* storage,
                                  u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_contract) * (size_t)capacity);
    }
}

static u32 agent_contract_find_index(const agent_contract_registry* reg,
                                     u64 contract_id,
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
        if (reg->entries[i].contract_id == contract_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->entries[i].contract_id > contract_id) {
            break;
        }
    }
    return i;
}

agent_contract* agent_contract_find(agent_contract_registry* reg,
                                    u64 contract_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->entries) {
        return 0;
    }
    idx = agent_contract_find_index(reg, contract_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->entries[idx];
}

int agent_contract_register(agent_contract_registry* reg,
                            u64 contract_id,
                            u64 party_a_id,
                            u64 party_b_id,
                            u32 allowed_process_mask_a,
                            u32 allowed_process_mask_b,
                            u32 required_authority_mask_a,
                            u32 required_authority_mask_b,
                            dom_act_time_t expiry_act,
                            dom_provenance_id provenance_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_contract* entry;
    if (!reg || !reg->entries || contract_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_contract_find_index(reg, contract_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->entries[i] = reg->entries[i - 1u];
    }
    entry = &reg->entries[idx];
    memset(entry, 0, sizeof(*entry));
    entry->contract_id = contract_id;
    entry->party_a_id = party_a_id;
    entry->party_b_id = party_b_id;
    entry->allowed_process_mask_a = allowed_process_mask_a;
    entry->allowed_process_mask_b = allowed_process_mask_b;
    entry->required_authority_mask_a = required_authority_mask_a;
    entry->required_authority_mask_b = required_authority_mask_b;
    entry->expiry_act = expiry_act;
    entry->failure_act = 0u;
    entry->status = AGENT_CONTRACT_ACTIVE;
    entry->flags = 0u;
    entry->provenance_id = provenance_id ? provenance_id : contract_id;
    reg->count += 1u;
    return 0;
}

int agent_contract_record_failure(agent_contract* contract,
                                  dom_act_time_t now_act)
{
    if (!contract) {
        return -1;
    }
    if (contract->status != AGENT_CONTRACT_ACTIVE) {
        return 0;
    }
    contract->status = AGENT_CONTRACT_FAILED;
    contract->failure_act = now_act;
    return 0;
}

int agent_contract_record_fulfilled(agent_contract* contract,
                                    dom_act_time_t now_act)
{
    if (!contract) {
        return -1;
    }
    if (contract->status != AGENT_CONTRACT_ACTIVE) {
        return 0;
    }
    contract->status = AGENT_CONTRACT_FULFILLED;
    contract->failure_act = now_act;
    return 0;
}

static u32 agent_contract_allowed_mask(const agent_contract* contract,
                                       u64 agent_id)
{
    if (!contract) {
        return 0u;
    }
    if (agent_id == contract->party_a_id) {
        return contract->allowed_process_mask_a;
    }
    if (agent_id == contract->party_b_id) {
        return contract->allowed_process_mask_b;
    }
    return 0u;
}

int agent_contract_check_plan(const agent_contract_registry* reg,
                              u64 agent_id,
                              const agent_plan* plan,
                              dom_act_time_t now_act,
                              u64* out_contract_id)
{
    u32 i;
    u32 step;
    if (out_contract_id) {
        *out_contract_id = 0u;
    }
    if (!reg || !reg->entries || !plan || agent_id == 0u) {
        return 1;
    }
    for (i = 0u; i < reg->count; ++i) {
        const agent_contract* c = &reg->entries[i];
        u32 mask;
        if (c->status != AGENT_CONTRACT_ACTIVE) {
            continue;
        }
        if (c->expiry_act != 0u && c->expiry_act <= now_act) {
            continue;
        }
        if (agent_id != c->party_a_id && agent_id != c->party_b_id) {
            continue;
        }
        mask = agent_contract_allowed_mask(c, agent_id);
        if (mask == 0u) {
            continue;
        }
        for (step = 0u; step < plan->step_count; ++step) {
            u32 kind = plan->steps[step].process_kind;
            if (kind == 0u) {
                continue;
            }
            if ((mask & AGENT_PROCESS_KIND_BIT(kind)) == 0u) {
                if (out_contract_id) {
                    *out_contract_id = c->contract_id;
                }
                return 0;
            }
        }
    }
    return 1;
}
