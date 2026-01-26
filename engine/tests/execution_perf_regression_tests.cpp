/*
Execution perf/determinism regression tests (EXEC-AUDIT1).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "domino/execution/task_graph.h"
#include "domino/execution/access_set.h"
#include "domino/execution/cost_model.h"
#include "domino/execution/execution_context.h"
#include "execution/scheduler/scheduler_single_thread.h"
#include "execution/scheduler/scheduler_parallel.h"

#define EXPECT(cond, msg) do { if (!(cond)) { \
    fprintf(stderr, "FAIL: %s\n", msg); \
    return 1; \
} } while (0)

#ifndef DOMINIUM_FIXTURES_DIR
#define DOMINIUM_FIXTURES_DIR "game/tests/fixtures"
#endif

typedef struct fixture_cfg {
    char name[64];
    u32 fixture_id;
    u32 strict_count;
    u32 ordered_count;
    u32 commutative_count;
    u32 derived_count;
    u32 phase_count;
    u32 shard_count;
    u32 total_regions;
    u32 active_regions;
    u32 tasks_per_region;
    u32 cpu_budget_2010;
    u32 cpu_budget_2020;
    u32 cpu_budget_server;
    u32 memory_budget_2010;
    u32 memory_budget_2020;
    u32 memory_budget_server;
    u32 event_budget;
    u32 bandwidth_budget;
    u32 degrade_cpu_budget;
    u64 expected_hash;
    u64 expected_degraded_hash;
} fixture_cfg;

typedef struct audit_log {
    dom_audit_event events[256];
    u32 count;
} audit_log;

typedef struct test_ctx {
    const dom_access_set *sets;
    u32 set_count;
    audit_log *audit;
} test_ctx;

static const dom_access_set *lookup_access_set(const dom_execution_context *ctx,
                                               u64 access_set_id,
                                               void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    u32 i;
    (void)ctx;
    if (!tctx || !tctx->sets) {
        return 0;
    }
    for (i = 0u; i < tctx->set_count; ++i) {
        if (tctx->sets[i].access_id == access_set_id) {
            return &tctx->sets[i];
        }
    }
    return 0;
}

static dom_law_decision law_accept_all(const dom_execution_context *ctx,
                                       const dom_task_node *node,
                                       void *user_data) {
    dom_law_decision decision;
    (void)ctx;
    (void)node;
    (void)user_data;
    decision.kind = DOM_LAW_ACCEPT;
    decision.refusal_code = 0u;
    decision.transformed_fidelity_tier = 0u;
    decision.transformed_next_due_tick = DOM_EXEC_TICK_INVALID;
    return decision;
}

static void record_audit(const dom_execution_context *ctx,
                         const dom_audit_event *event,
                         void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    (void)ctx;
    if (!tctx || !event || !tctx->audit) {
        return;
    }
    if (tctx->audit->count >= 256u) {
        return;
    }
    tctx->audit->events[tctx->audit->count] = *event;
    tctx->audit->count += 1u;
}

static void init_ctx(dom_execution_context *ctx, test_ctx *tctx) {
    ctx->act_now = 0u;
    ctx->scope_chain = 0;
    ctx->capability_sets = 0;
    ctx->budget_snapshot = 0;
    ctx->determinism_mode = DOM_DET_MODE_STRICT;
    ctx->evaluate_law = law_accept_all;
    ctx->record_audit = record_audit;
    ctx->lookup_access_set = lookup_access_set;
    ctx->user_data = tctx;
}

static u32 parse_u32(const char *text) {
    return (u32)strtoul(text, 0, 10);
}

static u64 parse_u64(const char *text) {
    return (u64)strtoull(text, 0, 10);
}

static void trim_line(char *line) {
    size_t len = strlen(line);
    while (len > 0u && (line[len - 1u] == '\n' || line[len - 1u] == '\r')) {
        line[len - 1u] = '\0';
        len -= 1u;
    }
}

static int parse_fixture(const char *path, fixture_cfg *cfg) {
    FILE *handle;
    char line[256];
    if (!cfg) {
        return -1;
    }
    memset(cfg, 0, sizeof(*cfg));
    handle = fopen(path, "r");
    if (!handle) {
        return -2;
    }
    while (fgets(line, sizeof(line), handle)) {
        char *eq;
        trim_line(line);
        if (line[0] == '\0' || line[0] == '#') {
            continue;
        }
        eq = strchr(line, '=');
        if (!eq) {
            continue;
        }
        *eq = '\0';
        const char *key = line;
        const char *value = eq + 1;
        if (strcmp(key, "name") == 0) {
            strncpy(cfg->name, value, sizeof(cfg->name) - 1u);
        } else if (strcmp(key, "fixture_id") == 0) {
            cfg->fixture_id = parse_u32(value);
        } else if (strcmp(key, "strict_count") == 0) {
            cfg->strict_count = parse_u32(value);
        } else if (strcmp(key, "ordered_count") == 0) {
            cfg->ordered_count = parse_u32(value);
        } else if (strcmp(key, "commutative_count") == 0) {
            cfg->commutative_count = parse_u32(value);
        } else if (strcmp(key, "derived_count") == 0) {
            cfg->derived_count = parse_u32(value);
        } else if (strcmp(key, "phase_count") == 0) {
            cfg->phase_count = parse_u32(value);
        } else if (strcmp(key, "shard_count") == 0) {
            cfg->shard_count = parse_u32(value);
        } else if (strcmp(key, "total_regions") == 0) {
            cfg->total_regions = parse_u32(value);
        } else if (strcmp(key, "active_regions") == 0) {
            cfg->active_regions = parse_u32(value);
        } else if (strcmp(key, "tasks_per_region") == 0) {
            cfg->tasks_per_region = parse_u32(value);
        } else if (strcmp(key, "cpu_budget_2010") == 0) {
            cfg->cpu_budget_2010 = parse_u32(value);
        } else if (strcmp(key, "cpu_budget_2020") == 0) {
            cfg->cpu_budget_2020 = parse_u32(value);
        } else if (strcmp(key, "cpu_budget_server") == 0) {
            cfg->cpu_budget_server = parse_u32(value);
        } else if (strcmp(key, "memory_budget_2010") == 0) {
            cfg->memory_budget_2010 = parse_u32(value);
        } else if (strcmp(key, "memory_budget_2020") == 0) {
            cfg->memory_budget_2020 = parse_u32(value);
        } else if (strcmp(key, "memory_budget_server") == 0) {
            cfg->memory_budget_server = parse_u32(value);
        } else if (strcmp(key, "event_budget") == 0) {
            cfg->event_budget = parse_u32(value);
        } else if (strcmp(key, "bandwidth_budget") == 0) {
            cfg->bandwidth_budget = parse_u32(value);
        } else if (strcmp(key, "degrade_cpu_budget") == 0) {
            cfg->degrade_cpu_budget = parse_u32(value);
        } else if (strcmp(key, "expected_hash") == 0) {
            cfg->expected_hash = parse_u64(value);
        } else if (strcmp(key, "expected_degraded_hash") == 0) {
            cfg->expected_degraded_hash = parse_u64(value);
        }
    }
    fclose(handle);
    return 0;
}

static u64 commit_hash(const audit_log *log) {
    u32 i;
    u64 hash = 0u;
    if (!log) {
        return 0u;
    }
    for (i = 0u; i < log->count; ++i) {
        if (log->events[i].event_id == DOM_EXEC_AUDIT_TASK_COMMITTED) {
            hash += log->events[i].task_id;
        }
    }
    return hash;
}

static void write_telemetry(const fixture_cfg *cfg,
                            u32 cpu_cost,
                            u32 memory_cost,
                            u32 event_depth,
                            u32 bandwidth_cost) {
    const char *run_root = getenv("DOMINIUM_RUN_ROOT");
    char path[256];
    FILE *handle;
    if (!cfg) {
        return;
    }
    if (!run_root || !run_root[0]) {
        run_root = ".";
    }
    snprintf(path, sizeof(path), "%s/perf_%s_telemetry.txt", run_root, cfg->name);
    handle = fopen(path, "w");
    if (!handle) {
        return;
    }
    fprintf(handle, "fixture=%s\n", cfg->name);
    fprintf(handle, "cpu_cost=%u\n", cpu_cost);
    fprintf(handle, "memory_cost=%u\n", memory_cost);
    fprintf(handle, "event_depth=%u\n", event_depth);
    fprintf(handle, "bandwidth_cost=%u\n", bandwidth_cost);
    fclose(handle);
}

static u32 total_tasks(const fixture_cfg *cfg) {
    if (!cfg) {
        return 0u;
    }
    return cfg->strict_count + cfg->ordered_count + cfg->commutative_count + cfg->derived_count;
}

static int build_graph(const fixture_cfg *cfg,
                       u32 task_limit,
                       dom_task_node *tasks,
                       u32 task_capacity,
                       dom_access_set *access_sets,
                       u32 access_capacity,
                       dom_access_range *ranges,
                       u32 range_capacity,
                       dom_cost_model *costs,
                       u32 cost_capacity,
                       dom_task_graph *out_graph,
                       u32 *out_access_count) {
    u32 i;
    u32 count = total_tasks(cfg);
    u32 range_index = 0u;
    static const u32 law_targets[1] = { 1u };
    if (!cfg || !tasks || !access_sets || !ranges || !costs || !out_graph) {
        return -1;
    }
    if (cfg->phase_count == 0u) {
        return -2;
    }
    if (task_limit > 0u && task_limit < count) {
        count = task_limit;
    }
    if (count > task_capacity || count > access_capacity || count > cost_capacity) {
        return -3;
    }
    for (i = 0u; i < count; ++i) {
        u64 task_id = (u64)cfg->fixture_id * 100000ULL + (u64)(i + 1u);
        u64 access_id = (u64)cfg->fixture_id * 1000000ULL + (u64)(i + 1u);
        u64 cost_id = access_id + 100u;
        u32 phase_id = (i % cfg->phase_count) + 1u;
        dom_task_node *node = &tasks[i];
        dom_access_set *set = &access_sets[i];
        dom_access_range *range = &ranges[range_index];
        dom_cost_model *cost = &costs[i];
        u32 category = (i < (cfg->strict_count + cfg->ordered_count + cfg->commutative_count))
                           ? DOM_TASK_AUTHORITATIVE
                           : DOM_TASK_DERIVED;
        u32 det_class = DOM_DET_STRICT;
        if (i >= cfg->strict_count && i < (cfg->strict_count + cfg->ordered_count)) {
            det_class = DOM_DET_ORDERED;
        } else if (i >= (cfg->strict_count + cfg->ordered_count) &&
                   i < (cfg->strict_count + cfg->ordered_count + cfg->commutative_count)) {
            det_class = DOM_DET_COMMUTATIVE;
        } else if (category == DOM_TASK_DERIVED) {
            det_class = DOM_DET_DERIVED;
        }

        node->task_id = task_id;
        node->system_id = cfg->fixture_id;
        node->category = category;
        node->determinism_class = det_class;
        node->fidelity_tier = DOM_FID_MACRO;
        node->next_due_tick = DOM_EXEC_TICK_INVALID;
        node->access_set_id = access_id;
        node->cost_model_id = cost_id;
        node->law_targets = (category == DOM_TASK_AUTHORITATIVE) ? law_targets : 0;
        node->law_target_count = (category == DOM_TASK_AUTHORITATIVE) ? 1u : 0u;
        node->phase_id = phase_id;
        node->commit_key.phase_id = phase_id;
        node->commit_key.task_id = task_id;
        node->commit_key.sub_index = 0u;
        node->law_scope_ref = 1u;
        node->actor_ref = 0u;
        node->capability_set_ref = 0u;
        node->policy_params = 0;
        node->policy_params_size = 0u;

        cost->cost_id = cost_id;
        cost->cpu_upper_bound = 1u;
        cost->memory_upper_bound = 1u;
        cost->bandwidth_upper_bound = 1u;
        cost->latency_class = DOM_LATENCY_LOW;
        cost->degradation_priority = 0;

        set->access_id = access_id;
        set->read_ranges = 0;
        set->read_count = 0u;
        set->write_ranges = 0;
        set->write_count = 0u;
        set->reduce_ranges = 0;
        set->reduce_count = 0u;
        set->reduction_op = DOM_REDUCE_NONE;
        set->commutative = D_FALSE;

        range->kind = DOM_RANGE_INDEX_RANGE;
        range->component_id = 200u + (u32)i;
        range->field_id = 1u;
        range->start_id = (u64)i;
        range->end_id = (u64)i;
        range->set_id = 0u;

        if (det_class == DOM_DET_COMMUTATIVE) {
            set->reduce_ranges = range;
            set->reduce_count = 1u;
            set->reduction_op = DOM_REDUCE_INT_SUM;
            set->commutative = D_TRUE;
        } else if (category == DOM_TASK_DERIVED) {
            set->read_ranges = range;
            set->read_count = 1u;
        } else {
            set->write_ranges = range;
            set->write_count = 1u;
        }

        range_index += 1u;
        if (range_index > range_capacity) {
            return -4;
        }
    }
    if (count > 1u) {
        dom_stable_task_sort(tasks, count);
    }
    out_graph->graph_id = cfg->fixture_id;
    out_graph->epoch_id = 1u;
    out_graph->tasks = tasks;
    out_graph->task_count = count;
    out_graph->dependency_edges = 0;
    out_graph->dependency_count = 0u;
    out_graph->phase_barriers = 0;
    out_graph->phase_barrier_count = 0u;
    if (out_access_count) {
        *out_access_count = count;
    }
    return 0;
}

static u64 run_graph(IScheduler &sched,
                     const dom_task_graph *graph,
                     const dom_access_set *sets,
                     u32 set_count) {
    dom_execution_context ctx;
    audit_log log;
    test_ctx tctx;
    log.count = 0u;
    tctx.sets = sets;
    tctx.set_count = set_count;
    tctx.audit = &log;
    init_ctx(&ctx, &tctx);
    class Sink : public IScheduleSink {
    public:
        virtual void on_task(const dom_task_node &, const dom_law_decision &) {}
    } sink;
    sched.schedule(*graph, ctx, sink);
    return commit_hash(&log);
}

static u64 run_stepwise(IScheduler &sched,
                        const fixture_cfg *cfg,
                        dom_task_node *tasks,
                        u32 task_count,
                        const dom_access_set *sets,
                        u32 set_count) {
    u32 phase;
    u64 hash = 0u;
    if (!cfg || !tasks || cfg->phase_count == 0u) {
        return 0u;
    }
    for (phase = 1u; phase <= cfg->phase_count; ++phase) {
        dom_task_node phase_tasks[128];
        dom_task_graph graph;
        u32 i;
        u32 count = 0u;
        for (i = 0u; i < task_count; ++i) {
            if (tasks[i].phase_id == phase) {
                phase_tasks[count++] = tasks[i];
            }
        }
        if (count == 0u) {
            continue;
        }
        dom_stable_task_sort(phase_tasks, count);
        graph.graph_id = cfg->fixture_id;
        graph.epoch_id = 1u;
        graph.tasks = phase_tasks;
        graph.task_count = count;
        graph.dependency_edges = 0;
        graph.dependency_count = 0u;
        graph.phase_barriers = 0;
        graph.phase_barrier_count = 0u;
        hash += run_graph(sched, &graph, sets, set_count);
    }
    return hash;
}

static int check_budgets(const fixture_cfg *cfg,
                         u32 cpu_cost,
                         u32 memory_cost,
                         u32 event_depth,
                         u32 bandwidth_cost) {
    if (!cfg) {
        return -1;
    }
    EXPECT(cpu_cost <= cfg->cpu_budget_2010, "cpu budget 2010 exceeded");
    EXPECT(cpu_cost <= cfg->cpu_budget_2020, "cpu budget 2020 exceeded");
    EXPECT(cpu_cost <= cfg->cpu_budget_server, "cpu budget server exceeded");
    EXPECT(memory_cost <= cfg->memory_budget_2010, "memory budget 2010 exceeded");
    EXPECT(memory_cost <= cfg->memory_budget_2020, "memory budget 2020 exceeded");
    EXPECT(memory_cost <= cfg->memory_budget_server, "memory budget server exceeded");
    EXPECT(event_depth <= cfg->event_budget, "event budget exceeded");
    EXPECT(bandwidth_cost <= cfg->bandwidth_budget, "bandwidth budget exceeded");
    return 0;
}

static int run_fixture(const char *fixture_name) {
    char path[256];
    fixture_cfg cfg;
    dom_task_node tasks[128];
    dom_access_set access_sets[128];
    dom_access_range ranges[128];
    dom_cost_model costs[128];
    dom_task_graph graph;
    u32 access_count = 0u;
    u32 count;
    u64 hash_batch;
    u64 hash_step;
    u64 hash_parallel;
    u64 hash_degraded;
    u32 cpu_cost;
    u32 memory_cost;
    u32 event_depth;
    u32 bandwidth_cost;
    dom_scheduler_single_thread sched_ref;
    dom_scheduler_parallel sched_par;

    snprintf(path, sizeof(path), "%s/%s/fixture.cfg", DOMINIUM_FIXTURES_DIR, fixture_name);
    EXPECT(parse_fixture(path, &cfg) == 0, "fixture parse failed");

    count = total_tasks(&cfg);
    EXPECT(count > 0u, "fixture task count zero");
    EXPECT(count <= 128u, "fixture task count exceeds capacity");
    if (cfg.total_regions > cfg.active_regions) {
        EXPECT(count <= cfg.active_regions * cfg.tasks_per_region, "global iteration guard failed");
    }

    EXPECT(build_graph(&cfg, 0u, tasks, 128u,
                       access_sets, 128u, ranges, 128u,
                       costs, 128u, &graph, &access_count) == 0, "graph build failed");

    hash_batch = run_graph(sched_ref, &graph, access_sets, access_count);
    hash_parallel = run_graph(sched_par, &graph, access_sets, access_count);
    hash_step = run_stepwise(sched_ref, &cfg, tasks, graph.task_count, access_sets, access_count);

    EXPECT(hash_batch == hash_parallel, "exec2 vs exec3 mismatch");
    EXPECT(hash_batch == hash_step, "step vs batch mismatch");
    if (hash_batch != cfg.expected_hash) {
        fprintf(stderr, "hash checkpoint mismatch fixture=%s expected=%llu got=%llu\n",
                cfg.name,
                (unsigned long long)cfg.expected_hash,
                (unsigned long long)hash_batch);
    }
    EXPECT(hash_batch == cfg.expected_hash, "hash checkpoint mismatch");

    cpu_cost = count;
    memory_cost = count * 2u;
    event_depth = count;
    bandwidth_cost = count * 4u;
    write_telemetry(&cfg, cpu_cost, memory_cost, event_depth, bandwidth_cost);
    EXPECT(check_budgets(&cfg, cpu_cost, memory_cost, event_depth, bandwidth_cost) == 0,
           "budget check failed");

    if (cfg.degrade_cpu_budget > 0u && cfg.degrade_cpu_budget < count) {
        EXPECT(build_graph(&cfg, cfg.degrade_cpu_budget, tasks, 128u,
                           access_sets, 128u, ranges, 128u,
                           costs, 128u, &graph, &access_count) == 0,
               "degraded graph build failed");
        hash_degraded = run_graph(sched_ref, &graph, access_sets, access_count);
        if (hash_degraded != cfg.expected_degraded_hash) {
            fprintf(stderr, "degraded hash mismatch fixture=%s expected=%llu got=%llu\n",
                    cfg.name,
                    (unsigned long long)cfg.expected_degraded_hash,
                    (unsigned long long)hash_degraded);
        }
        EXPECT(hash_degraded == cfg.expected_degraded_hash, "degraded hash mismatch");
    }
    return 0;
}

int main(void) {
    const char *fixtures[] = {
        "fixture_earth_only",
        "fixture_10k_systems_latent",
        "fixture_war_campaign",
        "fixture_market_crisis",
        "fixture_timewarp_1000y"
    };
    u32 i;
    for (i = 0u; i < sizeof(fixtures) / sizeof(fixtures[0]); ++i) {
        if (run_fixture(fixtures[i]) != 0) {
            return 1;
        }
    }
    return 0;
}
