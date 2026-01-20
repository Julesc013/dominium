/*
Economy Work IR migration tests (ADOPT4).
*/
#include "dominium/rules/economy/economy_system.h"
#include "dominium/rules/economy/ledger_tasks.h"
#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_graph.h"

#include <stdio.h>

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

static u64 fnv1a_u32(u64 h, u32 v)
{
    u32 i;
    for (i = 0u; i < 4u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 hash_ledger_state(const dom_ledger_state* ledger)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!ledger || !ledger->accounts) {
        return h;
    }
    h = fnv1a_u32(h, ledger->account_count);
    for (i = 0u; i < ledger->account_count; ++i) {
        h = fnv1a_u64(h, ledger->accounts[i].account_id);
        h = fnv1a_u64(h, (u64)ledger->accounts[i].balance);
    }
    return h;
}

static void init_economy_inputs(dom_economy_inputs* inputs,
                                const dom_ledger_transfer* transfers, u32 transfer_count,
                                const dom_contract_settlement* contracts, u32 contract_count,
                                const dom_production_step* production, u32 production_count,
                                const dom_consumption_step* consumption, u32 consumption_count,
                                const dom_maintenance_step* maintenance, u32 maintenance_count)
{
    if (!inputs) {
        return;
    }
    inputs->transfers = transfers;
    inputs->transfer_count = transfer_count;
    inputs->transfer_set_id = 6101u;
    inputs->contracts = contracts;
    inputs->contract_count = contract_count;
    inputs->contract_set_id = 6102u;
    inputs->production = production;
    inputs->production_count = production_count;
    inputs->production_set_id = 6103u;
    inputs->consumption = consumption;
    inputs->consumption_count = consumption_count;
    inputs->consumption_set_id = 6104u;
    inputs->maintenance = maintenance;
    inputs->maintenance_count = maintenance_count;
    inputs->maintenance_set_id = 6105u;
}

static int init_economy_buffers(dom_economy_buffers* buffers,
                                dom_ledger_state* ledger,
                                dom_ledger_account* accounts,
                                u32 account_capacity,
                                dom_economy_audit_log* audit,
                                dom_economy_audit_entry* audit_entries,
                                u32 audit_capacity)
{
    if (!buffers || !ledger || !audit) {
        return -1;
    }
    dom_ledger_state_init(ledger, accounts, account_capacity);
    dom_economy_audit_init(audit, audit_entries, audit_capacity, 1u);
    buffers->ledger = ledger;
    buffers->audit_log = audit;
    buffers->ledger_set_id = 6201u;
    buffers->audit_set_id = 6202u;
    return 0;
}

static int emit_graph(EconomySystem* system,
                      dom_work_graph_builder* graph_builder,
                      dom_access_set_builder* access_builder,
                      dom_task_graph* out_graph)
{
    if (!system || !graph_builder || !access_builder || !out_graph) {
        return -1;
    }
    dom_work_graph_builder_reset(graph_builder);
    dom_access_set_builder_reset(access_builder);
    dom_work_graph_builder_set_ids(graph_builder, 501u, 1u);
    if (system->emit_tasks(0, 10, graph_builder, access_builder) != 0) {
        return -2;
    }
    dom_work_graph_builder_finalize(graph_builder, out_graph);
    return 0;
}

static int execute_economy_graph(const dom_task_graph* graph,
                                 const dom_economy_inputs* inputs,
                                 dom_ledger_state* ledger,
                                 dom_economy_audit_log* audit)
{
    u32 i;
    if (!graph || !inputs || !ledger || !audit) {
        return -1;
    }
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        const dom_economy_task_params* params = (const dom_economy_task_params*)node->policy_params;
        if (!params || params->count == 0u) {
            continue;
        }
        switch (params->op) {
            case DOM_ECON_TASK_LEDGER_TRANSFERS:
                dom_ledger_apply_transfer_slice(ledger, inputs->transfers, inputs->transfer_count,
                                                params->start_index, params->count, audit);
                break;
            case DOM_ECON_TASK_CONTRACT_SETTLEMENT:
                dom_ledger_apply_contract_slice(ledger, inputs->contracts, inputs->contract_count,
                                                params->start_index, params->count, audit);
                break;
            case DOM_ECON_TASK_PRODUCTION_STEP:
                dom_ledger_apply_production_slice(ledger, inputs->production, inputs->production_count,
                                                  params->start_index, params->count, audit);
                break;
            case DOM_ECON_TASK_CONSUMPTION_STEP:
                dom_ledger_apply_consumption_slice(ledger, inputs->consumption, inputs->consumption_count,
                                                   params->start_index, params->count, audit);
                break;
            case DOM_ECON_TASK_MAINTENANCE_DECAY:
                dom_ledger_apply_maintenance_slice(ledger, inputs->maintenance, inputs->maintenance_count,
                                                   params->start_index, params->count, audit);
                break;
            default:
                return -2;
        }
    }
    return 0;
}

static int test_deterministic_progression(void)
{
    dom_ledger_transfer transfers[2] = {
        { 1u, 100u, 200u, 50 },
        { 2u, 200u, 300u, 30 }
    };
    dom_contract_settlement contracts[1] = {
        { 10u, 300u, 100u, 20 }
    };
    dom_production_step production[1] = { { 400u, 15 } };
    dom_consumption_step consumption[1] = { { 200u, 5 } };
    dom_maintenance_step maintenance[1] = { { 900u, 100u, 3 } };
    dom_economy_inputs inputs;
    dom_economy_buffers buffers_a;
    dom_economy_buffers buffers_b;
    dom_ledger_state ledger_a;
    dom_ledger_state ledger_b;
    dom_ledger_account accounts_a[8];
    dom_ledger_account accounts_b[8];
    dom_economy_audit_log audit_a;
    dom_economy_audit_log audit_b;
    dom_economy_audit_entry audit_entries_a[16];
    dom_economy_audit_entry audit_entries_b[16];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    EconomySystem system_a;
    EconomySystem system_b;
    u64 hash_a;
    u64 hash_b;

    init_economy_inputs(&inputs, transfers, 2u, contracts, 1u, production, 1u,
                        consumption, 1u, maintenance, 1u);
    EXPECT(init_economy_buffers(&buffers_a, &ledger_a, accounts_a, 8u, &audit_a, audit_entries_a, 16u) == 0, "buffers A");
    EXPECT(init_economy_buffers(&buffers_b, &ledger_b, accounts_b, 8u, &audit_b, audit_entries_b, 16u) == 0, "buffers B");

    system_a.init(&inputs, &buffers_a);
    system_b.init(&inputs, &buffers_b);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system_a, &graph_builder, &access_builder, &graph) == 0, "emit A");
    EXPECT(execute_economy_graph(&graph, &inputs, &ledger_a, &audit_a) == 0, "exec A");
    hash_a = hash_ledger_state(&ledger_a);

    EXPECT(emit_graph(&system_b, &graph_builder, &access_builder, &graph) == 0, "emit B");
    EXPECT(execute_economy_graph(&graph, &inputs, &ledger_b, &audit_b) == 0, "exec B");
    hash_b = hash_ledger_state(&ledger_b);

    EXPECT(hash_a == hash_b, "ledger determinism mismatch");
    return 0;
}

static int test_budget_compliance(void)
{
    dom_ledger_transfer transfers[3] = {
        { 1u, 10u, 20u, 5 },
        { 2u, 20u, 30u, 5 },
        { 3u, 30u, 40u, 5 }
    };
    dom_economy_inputs inputs;
    dom_economy_buffers buffers;
    dom_ledger_state ledger;
    dom_ledger_account accounts[8];
    dom_economy_audit_log audit;
    dom_economy_audit_entry audit_entries[16];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    EconomySystem system;
    u32 total = 0u;
    u32 i;

    init_economy_inputs(&inputs, transfers, 3u, 0, 0u, 0, 0u, 0, 0u, 0, 0u);
    EXPECT(init_economy_buffers(&buffers, &ledger, accounts, 8u, &audit, audit_entries, 16u) == 0, "buffers");
    system.init(&inputs, &buffers);
    system.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit budget");
    for (i = 0u; i < graph.task_count; ++i) {
        const dom_economy_task_params* params = (const dom_economy_task_params*)graph.tasks[i].policy_params;
        if (params) {
            total += params->count;
        }
    }
    EXPECT(total <= 1u, "budget exceeded");
    return 0;
}

static int test_law_gating(void)
{
    dom_ledger_transfer transfers[1] = { { 1u, 10u, 20u, 5 } };
    dom_economy_inputs inputs;
    dom_economy_buffers buffers;
    dom_ledger_state ledger;
    dom_ledger_account accounts[4];
    dom_economy_audit_log audit;
    dom_economy_audit_entry audit_entries[8];
    dom_task_node tasks[8];
    dom_dependency_edge deps[8];
    dom_phase_barrier barriers[2];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    EconomySystem system;

    init_economy_inputs(&inputs, transfers, 1u, 0, 0u, 0, 0u, 0, 0u, 0, 0u);
    EXPECT(init_economy_buffers(&buffers, &ledger, accounts, 4u, &audit, audit_entries, 8u) == 0, "buffers");
    system.init(&inputs, &buffers);
    system.set_allowed_ops_mask(0u);

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 8u, barriers, 2u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit gated");
    EXPECT(graph.task_count == 0u, "gated economy should emit no tasks");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    dom_ledger_transfer transfers[4] = {
        { 1u, 1u, 2u, 10 },
        { 2u, 2u, 3u, 10 },
        { 3u, 3u, 4u, 10 },
        { 4u, 4u, 1u, 10 }
    };
    dom_economy_inputs inputs;
    dom_economy_buffers buffers_batch;
    dom_economy_buffers buffers_step;
    dom_ledger_state ledger_batch;
    dom_ledger_state ledger_step;
    dom_ledger_account accounts_batch[8];
    dom_ledger_account accounts_step[8];
    dom_economy_audit_log audit_batch;
    dom_economy_audit_log audit_step;
    dom_economy_audit_entry audit_entries_batch[32];
    dom_economy_audit_entry audit_entries_step[32];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    EconomySystem system_batch;
    EconomySystem system_step;
    u64 hash_batch;
    u64 hash_step;
    u32 iterations = 0u;

    init_economy_inputs(&inputs, transfers, 4u, 0, 0u, 0, 0u, 0, 0u, 0, 0u);
    EXPECT(init_economy_buffers(&buffers_batch, &ledger_batch, accounts_batch, 8u,
                                &audit_batch, audit_entries_batch, 32u) == 0, "buffers batch");
    EXPECT(init_economy_buffers(&buffers_step, &ledger_step, accounts_step, 8u,
                                &audit_step, audit_entries_step, 32u) == 0, "buffers step");

    system_batch.init(&inputs, &buffers_batch);
    system_step.init(&inputs, &buffers_step);
    system_batch.set_budget_hint(16u);
    system_step.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system_batch, &graph_builder, &access_builder, &graph) == 0, "emit batch");
    EXPECT(execute_economy_graph(&graph, &inputs, &ledger_batch, &audit_batch) == 0, "exec batch");
    hash_batch = hash_ledger_state(&ledger_batch);

    while (iterations < 16u) {
        EXPECT(emit_graph(&system_step, &graph_builder, &access_builder, &graph) == 0, "emit step");
        if (graph.task_count == 0u) {
            break;
        }
        EXPECT(execute_economy_graph(&graph, &inputs, &ledger_step, &audit_step) == 0, "exec step");
        iterations += 1u;
    }
    hash_step = hash_ledger_state(&ledger_step);
    EXPECT(hash_batch == hash_step, "batch vs step mismatch");
    return 0;
}

static int test_auditability(void)
{
    dom_ledger_transfer transfers[1] = { { 1u, 5u, 6u, 7 } };
    dom_contract_settlement contracts[1] = { { 2u, 6u, 5u, 3 } };
    dom_production_step production[1] = { { 7u, 4 } };
    dom_consumption_step consumption[1] = { { 5u, 2 } };
    dom_maintenance_step maintenance[1] = { { 9u, 6u, 1 } };
    dom_economy_inputs inputs;
    dom_economy_buffers buffers;
    dom_ledger_state ledger;
    dom_ledger_account accounts[8];
    dom_economy_audit_log audit;
    dom_economy_audit_entry audit_entries[16];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    EconomySystem system;
    u32 expected = 5u;

    init_economy_inputs(&inputs, transfers, 1u, contracts, 1u, production, 1u,
                        consumption, 1u, maintenance, 1u);
    EXPECT(init_economy_buffers(&buffers, &ledger, accounts, 8u, &audit, audit_entries, 16u) == 0, "buffers");
    system.init(&inputs, &buffers);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit audit");
    EXPECT(execute_economy_graph(&graph, &inputs, &ledger, &audit) == 0, "exec audit");
    EXPECT(audit.count == expected, "audit count mismatch");
    return 0;
}

int main(void)
{
    if (test_deterministic_progression() != 0) return 1;
    if (test_budget_compliance() != 0) return 1;
    if (test_law_gating() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_auditability() != 0) return 1;
    return 0;
}
