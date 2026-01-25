/*
FILE: include/dominium/agents/agent_contract.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines agent contracts, obligations, and failure handling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Contracts ordered by contract_id.
*/
#ifndef DOMINIUM_AGENTS_AGENT_CONTRACT_H
#define DOMINIUM_AGENTS_AGENT_CONTRACT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/provenance.h"
#include "dominium/agents/agent_planner.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum agent_contract_status {
    AGENT_CONTRACT_ACTIVE = 0,
    AGENT_CONTRACT_FULFILLED = 1,
    AGENT_CONTRACT_FAILED = 2,
    AGENT_CONTRACT_REVOKED = 3
} agent_contract_status;

typedef struct agent_contract {
    u64 contract_id;
    u64 party_a_id;
    u64 party_b_id;
    u32 allowed_process_mask_a;
    u32 allowed_process_mask_b;
    u32 required_authority_mask_a;
    u32 required_authority_mask_b;
    dom_act_time_t expiry_act;
    dom_act_time_t failure_act;
    u32 status;
    u32 flags;
    dom_provenance_id provenance_id;
} agent_contract;

typedef struct agent_contract_registry {
    agent_contract* entries;
    u32 count;
    u32 capacity;
} agent_contract_registry;

void agent_contract_registry_init(agent_contract_registry* reg,
                                  agent_contract* storage,
                                  u32 capacity);
agent_contract* agent_contract_find(agent_contract_registry* reg,
                                    u64 contract_id);
int agent_contract_register(agent_contract_registry* reg,
                            u64 contract_id,
                            u64 party_a_id,
                            u64 party_b_id,
                            u32 allowed_process_mask_a,
                            u32 allowed_process_mask_b,
                            u32 required_authority_mask_a,
                            u32 required_authority_mask_b,
                            dom_act_time_t expiry_act,
                            dom_provenance_id provenance_id);
int agent_contract_record_failure(agent_contract* contract,
                                  dom_act_time_t now_act);
int agent_contract_record_fulfilled(agent_contract* contract,
                                    dom_act_time_t now_act);
int agent_contract_check_plan(const agent_contract_registry* reg,
                              u64 agent_id,
                              const agent_plan* plan,
                              dom_act_time_t now_act,
                              u64* out_contract_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_CONTRACT_H */
