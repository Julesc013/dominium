/*
Agent MVP social tests (AGENT2/TestX).
*/
#include "dominium/agents/agent_authority.h"
#include "dominium/agents/agent_conflict.h"
#include "dominium/agents/agent_constraint.h"
#include "dominium/agents/agent_contract.h"
#include "dominium/agents/agent_goal.h"
#include "dominium/agents/agent_history_macro.h"
#include "dominium/agents/agent_institution.h"
#include "dominium/agents/agent_planner.h"
#include "dominium/rules/agents/agent_planning_tasks.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static u64 fnv1a_init(void)
{
    return 1469598103934665603ULL;
}

static u64 fnv1a_u64(u64 h, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 hash_history(const agent_history_buffer* history)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!history || !history->entries) {
        return h;
    }
    h = fnv1a_u64(h, (u64)history->count);
    for (i = 0u; i < history->count; ++i) {
        const agent_history_record* rec = &history->entries[i];
        h = fnv1a_u64(h, rec->history_id);
        h = fnv1a_u64(h, rec->source_event_id);
        h = fnv1a_u64(h, rec->narrative_id);
        h = fnv1a_u64(h, rec->agent_id);
        h = fnv1a_u64(h, rec->institution_id);
        h = fnv1a_u64(h, rec->subject_id);
        h = fnv1a_u64(h, (u64)rec->act_time);
        h = fnv1a_u64(h, (u64)rec->kind);
        h = fnv1a_u64(h, (u64)rec->flags);
        h = fnv1a_u64(h, (u64)rec->amount);
    }
    return h;
}

static int test_institutions_are_agents(void)
{
    agent_institution storage[2];
    agent_institution_registry reg;
    agent_institution* inst;

    agent_institution_registry_init(&reg, storage, 2u);
    EXPECT(agent_institution_register(&reg, 1001u, 9001u,
                                      AGENT_AUTH_BASIC,
                                      50000u, 10u, 77u) == 0,
           "institution register");
    inst = agent_institution_find(&reg, 1001u);
    EXPECT(inst != 0, "institution lookup");
    EXPECT(inst->agent_id == 9001u, "institution agent id");
    EXPECT(inst->status == AGENT_INSTITUTION_ACTIVE, "institution active");
    return 0;
}

static int test_authority_grant_revoke(void)
{
    agent_authority_grant storage[2];
    agent_authority_registry reg;
    u32 mask;

    agent_authority_registry_init(&reg, storage, 2u);
    EXPECT(agent_authority_grant_register(&reg, 1u, 5000u, 6000u,
                                          AGENT_AUTH_TRADE, 0u, 88u) == 0,
           "authority grant");
    mask = agent_authority_effective_mask(&reg, 6000u, AGENT_AUTH_BASIC, 12u);
    EXPECT((mask & AGENT_AUTH_BASIC) != 0u, "base authority retained");
    EXPECT((mask & AGENT_AUTH_TRADE) != 0u, "grant authority applied");

    EXPECT(agent_authority_grant_revoke(&reg, 1u) == 0, "authority revoke");
    mask = agent_authority_effective_mask(&reg, 6000u, AGENT_AUTH_BASIC, 12u);
    EXPECT(mask == AGENT_AUTH_BASIC, "revoked authority removed");
    return 0;
}

static int test_constraints_block_actions(void)
{
    agent_constraint storage[2];
    agent_constraint_registry reg;
    u64 institution_id = 0u;
    int allowed;

    agent_constraint_registry_init(&reg, storage, 2u);
    EXPECT(agent_constraint_register(&reg, 10u, 2001u, 6000u,
                                     AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_TRADE),
                                     AGENT_CONSTRAINT_DENY,
                                     0u, 99u) == 0,
           "constraint register");
    allowed = agent_constraint_allows_process(&reg, 6000u,
                                              AGENT_PROCESS_KIND_TRADE,
                                              5u, &institution_id);
    EXPECT(allowed == 0, "constraint blocks process");
    EXPECT(institution_id == 2001u, "constraint institution id");
    allowed = agent_constraint_allows_process(&reg, 6000u,
                                              AGENT_PROCESS_KIND_MOVE,
                                              5u, 0);
    EXPECT(allowed != 0, "constraint allows unrelated process");

    EXPECT(agent_constraint_revoke(&reg, 10u) == 0, "constraint revoke");
    allowed = agent_constraint_allows_process(&reg, 6000u,
                                              AGENT_PROCESS_KIND_TRADE,
                                              5u, 0);
    EXPECT(allowed != 0, "revoked constraint allows");
    return 0;
}

static int test_contracts_bind_and_fail(void)
{
    agent_contract storage[2];
    agent_contract_registry reg;
    agent_contract* contract;
    agent_plan plan;
    u64 contract_id = 0u;
    int ok;

    agent_contract_registry_init(&reg, storage, 2u);
    EXPECT(agent_contract_register(&reg, 1u, 7000u, 7001u,
                                   AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_RESEARCH),
                                   AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_RESEARCH),
                                   0u, 0u, 0u, 123u) == 0,
           "contract register");

    memset(&plan, 0, sizeof(plan));
    plan.agent_id = 7000u;
    plan.step_count = 1u;
    plan.steps[0].process_kind = AGENT_PROCESS_KIND_TRADE;

    ok = agent_contract_check_plan(&reg, 7000u, &plan, 10u, &contract_id);
    EXPECT(ok == 0, "contract violation");
    EXPECT(contract_id == 1u, "contract id");
    contract = agent_contract_find(&reg, 1u);
    EXPECT(contract != 0, "contract lookup");
    EXPECT(agent_contract_record_failure(contract, 10u) == 0, "contract failure record");
    EXPECT(contract->status == AGENT_CONTRACT_FAILED, "contract failed status");

    EXPECT(agent_contract_register(&reg, 2u, 7000u, 7001u,
                                   AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_TRADE),
                                   AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_TRADE),
                                   0u, 0u, 0u, 124u) == 0,
           "contract register allowed");
    contract_id = 0u;
    ok = agent_contract_check_plan(&reg, 7000u, &plan, 10u, &contract_id);
    EXPECT(ok != 0, "contract allows plan");
    return 0;
}

static int test_conflict_and_collapse(void)
{
    agent_conflict conflict_storage[2];
    agent_conflict_registry conflict_reg;
    agent_conflict* conflict;
    agent_institution inst_storage[2];
    agent_institution_registry inst_reg;
    agent_institution* inst;

    agent_institution_registry_init(&inst_reg, inst_storage, 2u);
    EXPECT(agent_institution_register(&inst_reg, 4001u, 9001u,
                                      AGENT_AUTH_MILITARY,
                                      40000u, 12u, 221u) == 0,
           "institution register A");
    EXPECT(agent_institution_register(&inst_reg, 4002u, 9002u,
                                      AGENT_AUTH_MILITARY,
                                      40000u, 12u, 222u) == 0,
           "institution register B");

    agent_conflict_registry_init(&conflict_reg, conflict_storage, 2u);
    EXPECT(agent_conflict_register(&conflict_reg, 8001u, 9001u, 9002u,
                                   500u, 21u, 321u) == 0,
           "conflict register");
    conflict = agent_conflict_find(&conflict_reg, 8001u);
    EXPECT(conflict != 0, "conflict lookup");
    EXPECT(conflict->status == AGENT_CONFLICT_ACTIVE, "conflict active");
    EXPECT(agent_conflict_resolve(conflict, 33u) == 0, "conflict resolve");
    EXPECT(conflict->status == AGENT_CONFLICT_RESOLVED, "conflict resolved");
    EXPECT(conflict->resolved_act == 33u, "conflict resolved act");

    inst = agent_institution_find(&inst_reg, 4001u);
    EXPECT(inst != 0, "institution lookup for collapse");
    EXPECT(agent_institution_set_legitimacy(inst, 1u) == 0, "institution legitimacy set");
    EXPECT(agent_institution_check_collapse(inst, 10u, 44u) == 1, "institution collapse");
    EXPECT(inst->status == AGENT_INSTITUTION_COLLAPSED, "institution collapsed status");
    EXPECT(inst->collapsed_act == 44u, "institution collapse act");
    return 0;
}

static int test_history_macro_determinism(void)
{
    dom_agent_audit_entry audit_storage_a[4];
    dom_agent_audit_entry audit_storage_b[4];
    dom_agent_audit_log audit_a;
    dom_agent_audit_log audit_b;
    agent_history_record history_storage_a[8];
    agent_history_record history_storage_b[8];
    agent_history_buffer history_a;
    agent_history_buffer history_b;
    u64 narratives[1];
    agent_history_policy policy;
    u32 written_a;
    u32 written_b;
    u32 i;
    int saw_conflict = 0;
    int saw_collapse = 0;
    u64 hash_a;
    u64 hash_b;

    dom_agent_audit_init(&audit_a, audit_storage_a, 4u, 1u);
    dom_agent_audit_init(&audit_b, audit_storage_b, 4u, 1u);
    dom_agent_audit_set_context(&audit_a, 100u, 500u);
    dom_agent_audit_set_context(&audit_b, 100u, 500u);

    dom_agent_audit_record(&audit_a, 9001u, DOM_AGENT_AUDIT_CONFLICT_BEGIN,
                           8001u, 9002u, 1);
    dom_agent_audit_record(&audit_a, 9001u, DOM_AGENT_AUDIT_INSTITUTION_COLLAPSE,
                           4001u, 0u, -5);
    dom_agent_audit_record(&audit_b, 9001u, DOM_AGENT_AUDIT_CONFLICT_BEGIN,
                           8001u, 9002u, 1);
    dom_agent_audit_record(&audit_b, 9001u, DOM_AGENT_AUDIT_INSTITUTION_COLLAPSE,
                           4001u, 0u, -5);

    agent_history_buffer_init(&history_a, history_storage_a, 8u, 1u);
    agent_history_buffer_init(&history_b, history_storage_b, 8u, 1u);
    narratives[0] = 777u;
    memset(&policy, 0, sizeof(policy));
    policy.narrative_ids = narratives;
    policy.narrative_count = 1u;
    policy.include_objective = 1u;

    written_a = agent_history_aggregate(&audit_a, &policy, &history_a);
    written_b = agent_history_aggregate(&audit_b, &policy, &history_b);
    EXPECT(written_a == audit_a.count * 2u, "history count");
    EXPECT(written_a == written_b, "history determinism count");

    for (i = 0u; i < history_a.count; ++i) {
        if (history_a.entries[i].kind == DOM_AGENT_AUDIT_CONFLICT_BEGIN) {
            saw_conflict = 1;
        }
        if (history_a.entries[i].kind == DOM_AGENT_AUDIT_INSTITUTION_COLLAPSE) {
            saw_collapse = 1;
        }
    }
    EXPECT(saw_conflict != 0, "history conflict recorded");
    EXPECT(saw_collapse != 0, "history collapse recorded");

    hash_a = hash_history(&history_a);
    hash_b = hash_history(&history_b);
    EXPECT(hash_a == hash_b, "history determinism hash");
    return 0;
}

int main(void)
{
    if (test_institutions_are_agents() != 0) {
        return 1;
    }
    if (test_authority_grant_revoke() != 0) {
        return 1;
    }
    if (test_constraints_block_actions() != 0) {
        return 1;
    }
    if (test_contracts_bind_and_fail() != 0) {
        return 1;
    }
    if (test_conflict_and_collapse() != 0) {
        return 1;
    }
    if (test_history_macro_determinism() != 0) {
        return 1;
    }
    return 0;
}
