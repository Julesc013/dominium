/*
FILE: include/dominium/agents/delegation.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines delegation records and deterministic authority checks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Delegation resolution is ordered by delegation_id.
*/
#ifndef DOMINIUM_AGENTS_DELEGATION_H
#define DOMINIUM_AGENTS_DELEGATION_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/agents/agent_planner.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum agent_delegation_kind {
    AGENT_DELEGATION_GOAL = (1u << 0u),
    AGENT_DELEGATION_AUTHORITY = (1u << 1u)
} agent_delegation_kind;

typedef struct agent_delegation {
    u64 delegation_id;
    u64 delegator_ref;
    u64 delegatee_ref;
    u32 delegation_kind;
    u32 allowed_process_mask;
    u32 authority_mask;
    dom_act_time_t expiry_act;
    u64 provenance_ref;
    u32 revoked;
} agent_delegation;

typedef struct agent_delegation_registry {
    agent_delegation* delegations;
    u32 count;
    u32 capacity;
} agent_delegation_registry;

void agent_delegation_registry_init(agent_delegation_registry* reg,
                                    agent_delegation* storage,
                                    u32 capacity);
agent_delegation* agent_delegation_find(agent_delegation_registry* reg,
                                        u64 delegation_id);
agent_delegation* agent_delegation_find_for_delegatee(agent_delegation_registry* reg,
                                                      u64 delegatee_ref,
                                                      dom_act_time_t now_act);
int agent_delegation_register(agent_delegation_registry* reg,
                              u64 delegation_id,
                              u64 delegator_ref,
                              u64 delegatee_ref,
                              u32 delegation_kind,
                              u32 allowed_process_mask,
                              u32 authority_mask,
                              dom_act_time_t expiry_act,
                              u64 provenance_ref);
int agent_delegation_revoke(agent_delegation_registry* reg,
                            u64 delegation_id);
int agent_delegation_allows_process(const agent_delegation* delegation,
                                    u32 process_kind,
                                    dom_act_time_t now_act,
                                    agent_refusal_code* out_refusal);
int agent_delegation_check_plan(const agent_delegation_registry* reg,
                                u64 delegatee_ref,
                                const agent_plan* plan,
                                dom_act_time_t now_act,
                                agent_refusal_code* out_refusal);
int agent_cohort_plan_collapse(const agent_plan* plan,
                               u32 cohort_size,
                               agent_plan* out_plan);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_DELEGATION_H */
