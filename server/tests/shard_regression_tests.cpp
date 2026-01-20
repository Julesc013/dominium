/*
Shard regression tests (EXEC-AUDIT1).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "shard/task_splitter.h"
#include "execution/scheduler/scheduler_single_thread.h"
#include "domino/execution/access_set.h"

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
    u32 shard_count;
    u64 expected_hash;
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
        } else if (strcmp(key, "shard_count") == 0) {
            cfg->shard_count = parse_u32(value);
        } else if (strcmp(key, "expected_hash") == 0) {
            cfg->expected_hash = parse_u64(value);
        }
    }
    fclose(handle);
    return 0;
}

static u32 total_tasks(const fixture_cfg *cfg) {
    if (!cfg) {
        return 0u;
    }
    return cfg->strict_count + cfg->ordered_count + cfg->commutative_count + cfg->derived_count;
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

static u64 run_graph(dom_scheduler_single_thread &sched,
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

static u64 owner_id_for_task(u32 index, u32 shard_count) {
    const u64 range = 1000000ULL;
    u32 shard = (shard_count == 0u) ? 0u : (index % shard_count);
    return ((u64)(shard + 1u) * range) + (u64)(index + 1u);
}

static int build_graph(const fixture_cfg *cfg,
                       dom_task_node *tasks,
                       u32 task_capacity,
                       dom_access_set *access_sets,
                       u32 access_capacity,
                       dom_access_range *ranges,
                       u32 range_capacity,
                       dom_dependency_edge *edges,
                       u32 edge_capacity,
                       dom_task_graph *out_graph,
                       u32 *out_access_count,
                       u32 *out_edge_count) {
    u32 i;
    u32 count = total_tasks(cfg);
    u32 range_index = 0u;
    static const u32 law_targets[1] = { 1u };
    if (!cfg || !tasks || !access_sets || !ranges || !out_graph) {
        return -1;
    }
    if (count > task_capacity || count > access_capacity) {
        return -2;
    }
    if (count > 0u && edge_capacity < (count - 1u)) {
        return -3;
    }
    for (i = 0u; i < count; ++i) {
        u64 task_id = (u64)cfg->fixture_id * 100000ULL + (u64)(i + 1u);
        u64 access_id = (u64)cfg->fixture_id * 1000000ULL + (u64)(i + 1u);
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

        dom_task_node *node = &tasks[i];
        dom_access_set *set = &access_sets[i];
        dom_access_range *range = &ranges[range_index];
        u64 owner_id = owner_id_for_task(i, cfg->shard_count);

        node->task_id = task_id;
        node->system_id = cfg->fixture_id;
        node->category = category;
        node->determinism_class = det_class;
        node->fidelity_tier = DOM_FID_MACRO;
        node->next_due_tick = DOM_EXEC_TICK_INVALID;
        node->access_set_id = access_id;
        node->cost_model_id = access_id + 100u;
        node->law_targets = (category == DOM_TASK_AUTHORITATIVE) ? law_targets : 0;
        node->law_target_count = (category == DOM_TASK_AUTHORITATIVE) ? 1u : 0u;
        node->phase_id = 1u;
        node->commit_key.phase_id = 1u;
        node->commit_key.task_id = task_id;
        node->commit_key.sub_index = 0u;
        node->law_scope_ref = 1u;
        node->actor_ref = 0u;
        node->capability_set_ref = 0u;
        node->policy_params = 0;
        node->policy_params_size = 0u;

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
        range->component_id = 400u + (u32)i;
        range->field_id = 1u;
        range->start_id = owner_id;
        range->end_id = owner_id;
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
    for (i = 1u; i < count; ++i) {
        edges[i - 1u].from_task_id = tasks[i - 1u].task_id;
        edges[i - 1u].to_task_id = tasks[i].task_id;
        edges[i - 1u].reason_id = 0u;
    }
    out_graph->graph_id = cfg->fixture_id;
    out_graph->epoch_id = 1u;
    out_graph->tasks = tasks;
    out_graph->task_count = count;
    out_graph->dependency_edges = edges;
    out_graph->dependency_count = (count > 0u) ? (count - 1u) : 0u;
    out_graph->phase_barriers = 0;
    out_graph->phase_barrier_count = 0u;
    if (out_access_count) {
        *out_access_count = count;
    }
    if (out_edge_count) {
        *out_edge_count = out_graph->dependency_count;
    }
    return 0;
}

static int run_fixture(const char *fixture_name) {
    char path[256];
    fixture_cfg cfg;
    dom_task_node tasks[128];
    dom_access_set access_sets[128];
    dom_access_range ranges[128];
    dom_dependency_edge edges[128];
    dom_task_graph graph;
    u32 access_count = 0u;
    u32 edge_count = 0u;
    dom_scheduler_single_thread sched;
    u64 hash_unsharded;
    u64 hash_sharded = 0u;

    snprintf(path, sizeof(path), "%s/%s/fixture.cfg", DOMINIUM_FIXTURES_DIR, fixture_name);
    EXPECT(parse_fixture(path, &cfg) == 0, "fixture parse failed");
    if (cfg.shard_count < 2u) {
        return 0;
    }

    EXPECT(build_graph(&cfg, tasks, 128u, access_sets, 128u, ranges, 128u,
                       edges, 128u, &graph, &access_count, &edge_count) == 0,
           "graph build failed");
    hash_unsharded = run_graph(sched, &graph, access_sets, access_count);
    EXPECT(hash_unsharded == cfg.expected_hash, "unsharded hash mismatch");

    dom_shard_registry registry;
    dom_shard shards[4];
    dom_shard_task_graph shard_graphs[4];
    dom_task_node shard_tasks[4][128];
    dom_dependency_edge shard_edges[4][128];
    dom_shard_task_mapping mappings[128];
    dom_shard_message messages[128];
    dom_shard_task_splitter splitter;
    dom_execution_context ctx;
    test_ctx tctx;
    audit_log audit;
    u32 i;
    u32 shard_count = cfg.shard_count;
    const u64 range = 1000000ULL;

    EXPECT(shard_count <= 4u, "shard_count exceeds capacity");
    dom_shard_registry_init(&registry, shards, shard_count);
    for (i = 0u; i < shard_count; ++i) {
        dom_shard shard;
        shard.shard_id = i + 1u;
        shard.scope.kind = DOM_SHARD_SCOPE_ENTITY_RANGE;
        shard.scope.start_id = (u64)(i + 1u) * range;
        shard.scope.end_id = shard.scope.start_id + range - 1u;
        shard.scope.domain_tag = 0u;
        shard.determinism_domain = i + 1u;
        EXPECT(dom_shard_registry_add(&registry, &shard) == 0, "registry add");
    }

    for (i = 0u; i < shard_count; ++i) {
        dom_shard_task_graph_init(&shard_graphs[i], i + 1u,
                                  shard_tasks[i], 128u,
                                  shard_edges[i], 128u);
    }

    dom_shard_task_splitter_init(&splitter, shard_graphs, shard_count,
                                 mappings, 128u, messages, 128u);
    audit.count = 0u;
    tctx.sets = access_sets;
    tctx.set_count = access_count;
    tctx.audit = &audit;
    init_ctx(&ctx, &tctx);

    EXPECT(dom_shard_task_splitter_split(&splitter, &graph, &registry, &ctx, 1u) == 0,
           "splitter failed");
    if (edge_count > 0u) {
        EXPECT(splitter.message_count > 0u, "expected cross-shard messages");
    }
    for (i = 1u; i < splitter.message_count; ++i) {
        const dom_shard_message *prev = &splitter.messages[i - 1u];
        const dom_shard_message *cur = &splitter.messages[i];
        if (prev->arrival_tick > cur->arrival_tick) {
            return 1;
        }
        if (prev->arrival_tick == cur->arrival_tick &&
            prev->message_id > cur->message_id) {
            return 1;
        }
    }

    for (i = 0u; i < shard_count; ++i) {
        hash_sharded += run_graph(sched, &splitter.shard_graphs[i].graph,
                                  access_sets, access_count);
    }
    EXPECT(hash_sharded == hash_unsharded, "sharded hash mismatch");
    return 0;
}

int main(void) {
    const char *fixtures[] = {
        "fixture_10k_systems_latent",
        "fixture_war_campaign",
        "fixture_market_crisis"
    };
    u32 i;
    for (i = 0u; i < sizeof(fixtures) / sizeof(fixtures[0]); ++i) {
        if (run_fixture(fixtures[i]) != 0) {
            return 1;
        }
    }
    return 0;
}
