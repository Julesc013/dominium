/*
FILE: tools/mmo/mmo_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / mmo
RESPONSIBILITY: Deterministic MMO-1 runtime inspection scenarios.
*/
#include "mmo_cli.h"

#include "net/dom_server_runtime.h"
#include "net/dom_server_protocol.h"
#include "shard/dom_shard_lifecycle.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static u64 mmo_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static int mmo_parse_u32(const char* text, u32* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoul(text, &end, 10);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u32)value;
    return 1;
}

static u32 mmo_parse_workers(int argc, char** argv, u32 fallback)
{
    int i;
    u32 workers = fallback;
    if (workers == 0u) {
        workers = 1u;
    }
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--workers") == 0 && i + 1 < argc) {
            u32 parsed = 0u;
            if (mmo_parse_u32(argv[i + 1], &parsed) && parsed > 0u) {
                workers = parsed;
            }
        }
    }
    return workers;
}

static void mmo_config_default(dom_server_runtime_config* config, u32 shards, u32 workers)
{
    if (!config) {
        return;
    }
    dom_server_runtime_config_default(config);
    config->shard_count = shards ? shards : 1u;
    config->worker_count = workers ? workers : 1u;

    /* Keep budgets high for deterministic equivalence checks. */
    config->scale_budget_policy.active_domain_budget = 64u;
    config->scale_budget_policy.max_tier1_domains = 64u;
    config->scale_budget_policy.max_tier2_domains = 64u;
    config->scale_budget_policy.refinement_budget_per_tick = 1000000u;
    config->scale_budget_policy.refinement_cost_units = 1u;
    config->scale_budget_policy.planning_budget_per_tick = 1000000u;
    config->scale_budget_policy.planning_cost_units = 1u;
    config->scale_budget_policy.collapse_budget_per_tick = 1000000u;
    config->scale_budget_policy.expand_budget_per_tick = 1000000u;
    config->scale_budget_policy.collapse_cost_units = 1u;
    config->scale_budget_policy.expand_cost_units = 1u;
    config->scale_budget_policy.macro_event_budget_per_tick = 1000000u;
    config->scale_budget_policy.macro_event_cost_units = 1u;
    config->scale_budget_policy.compaction_budget_per_tick = 1000000u;
    config->scale_budget_policy.compaction_cost_units = 1u;
    config->scale_budget_policy.snapshot_budget_per_tick = 1000000u;
    config->scale_budget_policy.snapshot_cost_units = 1u;
    config->scale_budget_policy.macro_queue_limit = 1000000u;
    config->scale_budget_policy.deferred_queue_limit = DOM_SCALE_DEFER_QUEUE_CAP;
    config->scale_budget_policy.min_dwell_ticks = 0;
    config->macro_policy.macro_interval_ticks = 8;
    config->macro_policy.macro_event_kind = 1u;
    config->macro_policy.narrative_stride = 4u;
    config->checkpoint_policy.interval_ticks = 4u;
    config->checkpoint_policy.macro_event_stride = 4u;
    config->checkpoint_policy.checkpoint_before_transfer = 1u;
    config->checkpoint_policy.max_records = DOM_CHECKPOINT_MAX_RECORDS;
}

static int mmo_submit_intent(dom_server_runtime* runtime,
                             u64 client_id,
                             dom_shard_id shard_id,
                             u64 domain_id,
                             u32 kind,
                             u32 detail_code,
                             u32 payload_u32,
                             u32 payload_bytes,
                             u64 idempotency_key,
                             dom_act_time_t tick)
{
    dom_server_intent intent;
    memset(&intent, 0, sizeof(intent));
    intent.client_id = client_id;
    intent.target_shard_id = shard_id;
    intent.domain_id = domain_id;
    intent.intent_kind = kind;
    intent.detail_code = detail_code;
    intent.payload_u32 = payload_u32;
    intent.payload_bytes = payload_bytes;
    intent.idempotency_key = idempotency_key;
    intent.intent_tick = tick;
    return dom_server_runtime_submit_intent(runtime, &intent, payload_bytes);
}

static u64 mmo_owner_hash(const dom_server_runtime* runtime)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!runtime) {
        return hash;
    }
    hash = mmo_hash_mix(hash, runtime->owner_count);
    for (i = 0u; i < runtime->owner_count; ++i) {
        hash = mmo_hash_mix(hash, runtime->owners[i].domain_id);
        hash = mmo_hash_mix(hash, runtime->owners[i].owner_shard_id);
    }
    return hash;
}

static dom_shard_id mmo_owner_for_domain(const dom_server_runtime* runtime, u64 domain_id)
{
    u32 i;
    if (!runtime || domain_id == 0u) {
        return 0u;
    }
    for (i = 0u; i < runtime->owner_count; ++i) {
        if (runtime->owners[i].domain_id == domain_id) {
            return runtime->owners[i].owner_shard_id;
        }
    }
    return 0u;
}

static u64 mmo_scale_event_hash(const dom_scale_event_log* log)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!log || !log->events) {
        return hash;
    }
    hash = mmo_hash_mix(hash, log->count);
    hash = mmo_hash_mix(hash, log->overflow);
    for (i = 0u; i < log->count; ++i) {
        const dom_scale_event* ev = &log->events[i];
        hash = mmo_hash_mix(hash, ev->kind);
        hash = mmo_hash_mix(hash, ev->domain_id);
        hash = mmo_hash_mix(hash, ev->domain_kind);
        hash = mmo_hash_mix(hash, ev->capsule_id);
        hash = mmo_hash_mix(hash, ev->reason_code);
        hash = mmo_hash_mix(hash, ev->refusal_code);
        hash = mmo_hash_mix(hash, ev->defer_code);
        hash = mmo_hash_mix(hash, ev->detail_code);
        hash = mmo_hash_mix(hash, ev->seed_value);
        hash = mmo_hash_mix(hash, ev->budget_kind);
        hash = mmo_hash_mix(hash, ev->budget_limit);
        hash = mmo_hash_mix(hash, ev->budget_used);
        hash = mmo_hash_mix(hash, ev->budget_cost);
        hash = mmo_hash_mix(hash, ev->budget_queue);
        hash = mmo_hash_mix(hash, ev->budget_overflow);
        hash = mmo_hash_mix(hash, (u64)ev->tick);
    }
    return hash;
}

static u64 mmo_state_hash_no_checkpoint(const dom_server_runtime* runtime)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!runtime) {
        return hash;
    }
    hash = mmo_hash_mix(hash, runtime->now_tick);
    hash = mmo_hash_mix(hash, runtime->shard_count);
    hash = mmo_hash_mix(hash, runtime->message_sequence);
    hash = mmo_hash_mix(hash, runtime->message_applied);
    hash = mmo_hash_mix(hash, runtime->macro_events_executed);
    hash = mmo_hash_mix(hash, mmo_owner_hash(runtime));
    hash = mmo_hash_mix(hash, dom_shard_lifecycle_log_hash(&runtime->lifecycle_log));
    for (i = 0u; i < runtime->shard_count; ++i) {
        const dom_server_shard* shard = &runtime->shards[i];
        u32 d;
        hash = mmo_hash_mix(hash, shard->shard_id);
        hash = mmo_hash_mix(hash, shard->lifecycle_state);
        hash = mmo_hash_mix(hash, shard->version_id);
        hash = mmo_hash_mix(hash, shard->capability_mask);
        hash = mmo_hash_mix(hash, shard->baseline_hash);
        hash = mmo_hash_mix(hash, mmo_scale_event_hash(&shard->scale_event_log));
        for (d = 0u; d < shard->scale_ctx.domain_count; ++d) {
            const dom_scale_domain_slot* slot = &shard->scale_ctx.domains[d];
            hash = mmo_hash_mix(hash,
                                dom_scale_domain_hash(slot,
                                                      runtime->now_tick,
                                                      1u));
        }
    }
    return hash;
}

static u32 mmo_count_refusals(const dom_server_runtime* runtime, u32 refusal_code)
{
    u32 i;
    u32 count = 0u;
    if (!runtime) {
        return 0u;
    }
    for (i = 0u; i < runtime->event_count; ++i) {
        if (runtime->events[i].refusal_code == refusal_code) {
            count += 1u;
        }
    }
    return count;
}

static int mmo_run_two_node(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* a = 0;
    dom_server_runtime* b = 0;
    u64 domain_a = 0u;
    u64 domain_b = 0u;
    u64 hash_a = 0u;
    u64 hash_b = 0u;
    u32 refusals_a = 0u;
    u32 refusals_b = 0u;

    mmo_config_default(&config, 2u, workers);
    a = (dom_server_runtime*)calloc(1u, sizeof(*a));
    b = (dom_server_runtime*)calloc(1u, sizeof(*b));
    if (!a || !b) {
        fprintf(stderr, "mmo: failed to allocate runtimes\n");
        free(a);
        free(b);
        return 2;
    }
    if (dom_server_runtime_init(a, &config) != 0 ||
        dom_server_runtime_init(b, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtimes\n");
        free(a);
        free(b);
        return 2;
    }
    (void)dom_server_runtime_add_client(a, 101u, 1u, 0);
    (void)dom_server_runtime_add_client(a, 202u, 2u, 0);
    (void)dom_server_runtime_add_client(b, 101u, 1u, 0);
    (void)dom_server_runtime_add_client(b, 202u, 2u, 0);

    domain_a = a->shards[0].domain_storage[0].domain_id;
    domain_b = a->shards[1].domain_storage[0].domain_id;

    (void)mmo_submit_intent(a, 101u, 1u, domain_a, DOM_SERVER_INTENT_COLLAPSE, 11u, 0u, 8u, 1001u, 0);
    (void)mmo_submit_intent(a, 202u, 2u, domain_b, DOM_SERVER_INTENT_COLLAPSE, 12u, 0u, 8u, 2001u, 0);
    (void)mmo_submit_intent(a, 101u, 1u, domain_a, DOM_SERVER_INTENT_EXPAND, 21u, 0u, 8u, 1002u, 1);
    (void)mmo_submit_intent(a, 101u, 1u, domain_a, DOM_SERVER_INTENT_TRANSFER_OWNERSHIP, 0u, 2u, 8u, 3001u, 2);

    /* Submit in a different order; runtime sorting must normalize it. */
    (void)mmo_submit_intent(b, 101u, 1u, domain_a, DOM_SERVER_INTENT_TRANSFER_OWNERSHIP, 0u, 2u, 8u, 3001u, 2);
    (void)mmo_submit_intent(b, 101u, 1u, domain_a, DOM_SERVER_INTENT_EXPAND, 21u, 0u, 8u, 1002u, 1);
    (void)mmo_submit_intent(b, 202u, 2u, domain_b, DOM_SERVER_INTENT_COLLAPSE, 12u, 0u, 8u, 2001u, 0);
    (void)mmo_submit_intent(b, 101u, 1u, domain_a, DOM_SERVER_INTENT_COLLAPSE, 11u, 0u, 8u, 1001u, 0);

    (void)dom_server_runtime_tick(a, 4);
    (void)dom_server_runtime_tick(b, 4);

    hash_a = dom_server_runtime_hash(a);
    hash_b = dom_server_runtime_hash(b);
    refusals_a = mmo_count_refusals(a, DOM_SERVER_REFUSE_NONE);
    refusals_b = mmo_count_refusals(b, DOM_SERVER_REFUSE_NONE);

    printf("scenario=two_node workers=%u invariants=%s\n",
           (unsigned int)workers,
           "SCALE0-DETERMINISM-004,MMO0-UNIVERSE-012,MMO0-LOG-015,MMO0-TIME-016");
    printf("two_node.hash_a=%llu two_node.hash_b=%llu two_node.hash_match=%u\n",
           (unsigned long long)hash_a,
           (unsigned long long)hash_b,
           (unsigned int)(hash_a == hash_b ? 1u : 0u));
    printf("two_node.owner_hash_a=%llu two_node.owner_hash_b=%llu\n",
           (unsigned long long)mmo_owner_hash(a),
           (unsigned long long)mmo_owner_hash(b));
    printf("two_node.events_a=%u two_node.events_b=%u refusals_none_a=%u refusals_none_b=%u\n",
           (unsigned int)a->event_count,
           (unsigned int)b->event_count,
           (unsigned int)refusals_a,
           (unsigned int)refusals_b);
    free(a);
    free(b);
    return (hash_a == hash_b) ? 0 : 1;
}

static int mmo_run_join_resync(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* runtime = 0;
    dom_server_join_bundle join_bundle;
    dom_server_resync_bundle resync_bundle;
    u64 domain_id = 0u;
    u64 hash_after = 0u;
    int resync_status = 0;

    mmo_config_default(&config, 2u, workers);
    runtime = (dom_server_runtime*)calloc(1u, sizeof(*runtime));
    if (!runtime) {
        fprintf(stderr, "mmo: failed to allocate runtime\n");
        return 2;
    }
    if (dom_server_runtime_init(runtime, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtime\n");
        free(runtime);
        return 2;
    }
    (void)dom_server_runtime_add_client(runtime, 501u, 1u, 0);
    domain_id = runtime->shards[0].domain_storage[0].domain_id;

    (void)mmo_submit_intent(runtime, 501u, 1u, domain_id, DOM_SERVER_INTENT_COLLAPSE, 9u, 0u, 8u, 9001u, 0);
    (void)mmo_submit_intent(runtime, 501u, 1u, domain_id, DOM_SERVER_INTENT_EXPAND, 10u, 0u, 8u, 9002u, 1);
    (void)dom_server_runtime_tick(runtime, 3);

    (void)dom_server_runtime_join(runtime, 501u, &join_bundle);
    resync_status = dom_server_runtime_resync(runtime, 501u, 1u, 1u, &resync_bundle);
    hash_after = dom_server_runtime_hash(runtime);

    printf("scenario=join_resync workers=%u invariants=%s\n",
           (unsigned int)workers,
           "MMO0-RESYNC-017,MMO0-COMPAT-018,SCALE0-DETERMINISM-004");
    printf("join.world_hash=%llu join.capability_hash=%llu join.inspect_only=%u\n",
           (unsigned long long)join_bundle.world_hash,
           (unsigned long long)join_bundle.capability_hash,
           (unsigned int)join_bundle.inspect_only);
    printf("resync.status=%d resync.refusal=%s resync.world_hash=%llu\n",
           resync_status,
           dom_server_refusal_to_string(resync_bundle.refusal_code),
           (unsigned long long)resync_bundle.world_hash);
    printf("resync.hash_match=%u event_tail=%u message_tail=%u\n",
           (unsigned int)(hash_after == resync_bundle.world_hash ? 1u : 0u),
           (unsigned int)resync_bundle.event_tail_index,
           (unsigned int)resync_bundle.message_tail_index);
    free(runtime);
    return (hash_after == resync_bundle.world_hash) ? 0 : 1;
}

static int mmo_run_abuse(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* runtime = 0;
    dom_server_client_policy policy;
    dom_scale_budget_snapshot scale_snapshot;
    u64 domain_id = 0u;
    u32 refusal_rate = 0u;
    u32 refusal_budget = 0u;

    mmo_config_default(&config, 1u, workers);
    runtime = (dom_server_runtime*)calloc(1u, sizeof(*runtime));
    if (!runtime) {
        fprintf(stderr, "mmo: failed to allocate runtime\n");
        return 2;
    }
    if (dom_server_runtime_init(runtime, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtime\n");
        free(runtime);
        return 2;
    }
    memset(&policy, 0, sizeof(policy));
    policy.intents_per_tick = 1u;
    policy.bytes_per_tick = 4u;
    policy.inspect_only = 0u;
    policy.capability_mask = 1u;
    (void)dom_server_runtime_add_client(runtime, 601u, 1u, &policy);
    domain_id = runtime->shards[0].domain_storage[0].domain_id;

    (void)mmo_submit_intent(runtime, 601u, 1u, domain_id, DOM_SERVER_INTENT_COLLAPSE, 1u, 0u, 4u, 1u, 0);
    (void)mmo_submit_intent(runtime, 601u, 1u, domain_id, DOM_SERVER_INTENT_EXPAND, 2u, 0u, 4u, 2u, 0);
    (void)mmo_submit_intent(runtime, 601u, 1u, domain_id, DOM_SERVER_INTENT_COLLAPSE, 3u, 0u, 4u, 3u, 0);
    (void)dom_server_runtime_tick(runtime, 1);

    refusal_rate = mmo_count_refusals(runtime, DOM_SERVER_REFUSE_RATE_LIMIT);
    refusal_budget = mmo_count_refusals(runtime, DOM_SERVER_REFUSE_BUDGET_EXCEEDED);
    (void)dom_server_runtime_scale_snapshot(runtime, 1u, &scale_snapshot);

    printf("scenario=abuse workers=%u invariants=%s\n",
           (unsigned int)workers,
           "SCALE3-BUDGET-009,SCALE3-ADMISSION-010,SCALE0-DETERMINISM-004");
    printf("abuse.refusal_rate_limit=%u abuse.refusal_budget=%u events=%u\n",
           (unsigned int)refusal_rate,
           (unsigned int)refusal_budget,
           (unsigned int)runtime->event_count);
    printf("budget.tick=%lld macro_used=%u macro_limit=%u deferred=%u\n",
           (long long)scale_snapshot.tick,
           (unsigned int)scale_snapshot.macro_event_used,
           (unsigned int)scale_snapshot.macro_event_limit,
           (unsigned int)scale_snapshot.deferred_count);
    free(runtime);
    return (refusal_rate > 0u) ? 0 : 1;
}

static int mmo_run_legacy(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* runtime = 0;
    dom_server_client_policy policy;
    dom_server_join_bundle join_bundle;
    dom_server_resync_bundle resync_bundle;
    u64 domain_id = 0u;
    u32 refusal_cap = 0u;

    mmo_config_default(&config, 1u, workers);
    runtime = (dom_server_runtime*)calloc(1u, sizeof(*runtime));
    if (!runtime) {
        fprintf(stderr, "mmo: failed to allocate runtime\n");
        return 2;
    }
    if (dom_server_runtime_init(runtime, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtime\n");
        free(runtime);
        return 2;
    }
    memset(&policy, 0, sizeof(policy));
    policy.intents_per_tick = 8u;
    policy.bytes_per_tick = 64u;
    policy.inspect_only = 1u;
    policy.capability_mask = 0u;
    (void)dom_server_runtime_add_client(runtime, 701u, 1u, &policy);
    domain_id = runtime->shards[0].domain_storage[0].domain_id;

    (void)mmo_submit_intent(runtime, 701u, 1u, domain_id, DOM_SERVER_INTENT_COLLAPSE, 1u, 0u, 4u, 7001u, 0);
    (void)dom_server_runtime_tick(runtime, 1);
    refusal_cap = mmo_count_refusals(runtime, DOM_SERVER_REFUSE_CAPABILITY_MISSING);

    (void)dom_server_runtime_join(runtime, 701u, &join_bundle);
    (void)dom_server_runtime_resync(runtime, 701u, 1u, 0u, &resync_bundle);

    printf("scenario=legacy workers=%u invariants=%s\n",
           (unsigned int)workers,
           "MMO0-COMPAT-018,MMO0-RESYNC-017,SCALE0-DETERMINISM-004");
    printf("legacy.inspect_only=%u legacy.refusal_capability=%u\n",
           (unsigned int)join_bundle.inspect_only,
           (unsigned int)refusal_cap);
    printf("legacy.resync_refusal=%s legacy.world_hash=%llu\n",
           dom_server_refusal_to_string(resync_bundle.refusal_code),
           (unsigned long long)resync_bundle.world_hash);
    free(runtime);
    return (refusal_cap > 0u && resync_bundle.refusal_code != 0u) ? 0 : 1;
}

static int mmo_run_ops_checkpoint(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* runtime = 0;
    const dom_checkpoint_record* record = 0;
    u64 domain_a = 0u;
    u64 domain_b = 0u;
    u64 state_hash = 0u;
    u64 store_hash = 0u;
    u32 i;

    mmo_config_default(&config, 2u, workers);
    runtime = (dom_server_runtime*)calloc(1u, sizeof(*runtime));
    if (!runtime) {
        fprintf(stderr, "mmo: failed to allocate runtime\n");
        return 2;
    }
    if (dom_server_runtime_init(runtime, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtime\n");
        free(runtime);
        return 2;
    }
    (void)dom_server_runtime_add_client(runtime, 801u, 1u, 0);
    (void)dom_server_runtime_add_client(runtime, 802u, 2u, 0);
    domain_a = runtime->shards[0].domain_storage[0].domain_id;
    domain_b = runtime->shards[1].domain_storage[0].domain_id;

    (void)mmo_submit_intent(runtime, 801u, 1u, domain_a, DOM_SERVER_INTENT_COLLAPSE, 31u, 0u, 8u, 8101u, 0);
    (void)mmo_submit_intent(runtime, 801u, 1u, domain_a, DOM_SERVER_INTENT_EXPAND, 32u, 0u, 8u, 8102u, 1);
    (void)mmo_submit_intent(runtime, 802u, 2u, domain_b, DOM_SERVER_INTENT_COLLAPSE, 33u, 0u, 8u, 8201u, 0);
    (void)dom_server_runtime_tick(runtime, 4);

    if (dom_server_runtime_checkpoint(runtime, DOM_CHECKPOINT_TRIGGER_MANUAL) != 0) {
        fprintf(stderr, "mmo: checkpoint refused\n");
        free(runtime);
        return 1;
    }
    record = dom_server_runtime_last_checkpoint(runtime);
    if (!record) {
        fprintf(stderr, "mmo: no checkpoint record\n");
        free(runtime);
        return 1;
    }

    state_hash = mmo_state_hash_no_checkpoint(runtime);
    store_hash = dom_server_runtime_checkpoint_hash(runtime);

    printf("scenario=ops_checkpoint workers=%u invariants=%s\n",
           (unsigned int)workers,
           "MMO2-CHECKPOINT-001,MMO2-LOG-006,MMO2-LIFECYCLE-003,SCALE0-DETERMINISM-004");
    printf("checkpoint.id=%llu checkpoint.tick=%lld checkpoint.runtime_hash=%llu checkpoint.store_hash=%llu state_hash=%llu\n",
           (unsigned long long)record->manifest.checkpoint_id,
           (long long)record->manifest.tick,
           (unsigned long long)record->manifest.runtime_hash,
           (unsigned long long)store_hash,
           (unsigned long long)state_hash);
    printf("checkpoint.msg_seq=%llu checkpoint.msg_applied=%llu checkpoint.macro_events=%llu lifecycle_count=%u\n",
           (unsigned long long)record->manifest.message_sequence,
           (unsigned long long)record->manifest.message_applied,
           (unsigned long long)record->manifest.macro_events_executed,
           (unsigned int)record->lifecycle_count);
    for (i = 0u; i < runtime->shard_count; ++i) {
        const dom_shard_checkpoint* shard = &record->shards[i];
        printf("shard.%u id=%u state=%s version=%u caps=%llu shard_hash=%llu world_checksum=%llu\n",
               (unsigned int)i,
               (unsigned int)shard->shard_id,
               dom_shard_lifecycle_state_name(shard->lifecycle_state),
               (unsigned int)shard->version_id,
               (unsigned long long)shard->capability_mask,
               (unsigned long long)shard->shard_hash,
               (unsigned long long)shard->world_checksum);
    }
    free(runtime);
    return 0;
}

static int mmo_run_ops_recover(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* runtime = 0;
    dom_server_runtime* shadow = 0;
    const dom_checkpoint_record* record = 0;
    u64 domain_id = 0u;
    u64 state_hash_checkpoint = 0u;
    u64 state_hash_before = 0u;
    u64 state_hash_after = 0u;
    u64 state_hash_shadow = 0u;
    u32 refusal = DOM_SERVER_REFUSE_NONE;
    u32 refusal_shadow = DOM_SERVER_REFUSE_NONE;

    mmo_config_default(&config, 2u, workers);
    runtime = (dom_server_runtime*)calloc(1u, sizeof(*runtime));
    shadow = (dom_server_runtime*)calloc(1u, sizeof(*shadow));
    if (!runtime || !shadow) {
        fprintf(stderr, "mmo: failed to allocate runtimes\n");
        free(runtime);
        free(shadow);
        return 2;
    }
    if (dom_server_runtime_init(runtime, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtime\n");
        free(runtime);
        free(shadow);
        return 2;
    }
    (void)dom_server_runtime_add_client(runtime, 901u, 1u, 0);
    domain_id = runtime->shards[0].domain_storage[0].domain_id;

    (void)mmo_submit_intent(runtime, 901u, 1u, domain_id, DOM_SERVER_INTENT_COLLAPSE, 41u, 0u, 8u, 9101u, 0);
    (void)mmo_submit_intent(runtime, 901u, 1u, domain_id, DOM_SERVER_INTENT_EXPAND, 42u, 0u, 8u, 9102u, 1);
    (void)dom_server_runtime_tick(runtime, 3);

    if (dom_server_runtime_checkpoint(runtime, DOM_CHECKPOINT_TRIGGER_MANUAL) != 0) {
        fprintf(stderr, "mmo: checkpoint refused\n");
        free(runtime);
        free(shadow);
        return 1;
    }
    record = dom_server_runtime_last_checkpoint(runtime);
    if (!record) {
        fprintf(stderr, "mmo: no checkpoint record\n");
        free(runtime);
        free(shadow);
        return 1;
    }

    state_hash_checkpoint = mmo_state_hash_no_checkpoint(runtime);
    (void)mmo_submit_intent(runtime, 901u, 1u, domain_id, DOM_SERVER_INTENT_COLLAPSE, 43u, 0u, 8u, 9103u, 4);
    (void)dom_server_runtime_tick(runtime, 6);
    state_hash_before = mmo_state_hash_no_checkpoint(runtime);

    (void)dom_checkpoint_recover(runtime, record, &refusal);
    state_hash_after = mmo_state_hash_no_checkpoint(runtime);

    if (dom_server_runtime_init(shadow, &config) != 0) {
        fprintf(stderr, "mmo: failed to init shadow runtime\n");
        free(runtime);
        free(shadow);
        return 2;
    }
    (void)dom_checkpoint_recover(shadow, record, &refusal_shadow);
    state_hash_shadow = mmo_state_hash_no_checkpoint(shadow);

    printf("scenario=ops_recover workers=%u invariants=%s\n",
           (unsigned int)workers,
           "MMO2-RECOVERY-002,MMO2-CHECKPOINT-001,SCALE0-DETERMINISM-004");
    printf("recover.checkpoint_hash=%llu recover.before_hash=%llu recover.after_hash=%llu recover.shadow_hash=%llu\n",
           (unsigned long long)state_hash_checkpoint,
           (unsigned long long)state_hash_before,
           (unsigned long long)state_hash_after,
           (unsigned long long)state_hash_shadow);
    printf("recover.tick_checkpoint=%lld recover.tick_after=%lld refusal=%s shadow_refusal=%s\n",
           (long long)record->manifest.tick,
           (long long)runtime->now_tick,
           dom_server_refusal_to_string(refusal),
           dom_server_refusal_to_string(refusal_shadow));
    {
        const dom_act_time_t runtime_tick = runtime->now_tick;
        const dom_act_time_t checkpoint_tick = record->manifest.tick;
        const int ok = (refusal == DOM_SERVER_REFUSE_NONE &&
                        refusal_shadow == DOM_SERVER_REFUSE_NONE &&
                        runtime_tick == checkpoint_tick &&
                        state_hash_after == state_hash_shadow &&
                        state_hash_after == state_hash_checkpoint) ? 0 : 1;
        free(runtime);
        free(shadow);
        return ok;
    }
}

static int mmo_run_ops_shards(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* runtime = 0;
    u64 domain_id = 0u;
    dom_shard_id owner_after = 0u;
    u32 refusal_gap = 0u;
    u32 refusal_state = 0u;

    mmo_config_default(&config, 2u, workers);
    runtime = (dom_server_runtime*)calloc(1u, sizeof(*runtime));
    if (!runtime) {
        fprintf(stderr, "mmo: failed to allocate runtime\n");
        return 2;
    }
    if (dom_server_runtime_init(runtime, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtime\n");
        free(runtime);
        return 2;
    }
    (void)dom_server_runtime_add_client(runtime, 1001u, 1u, 0);
    (void)dom_server_runtime_add_client(runtime, 1002u, 2u, 0);
    domain_id = runtime->shards[0].domain_storage[0].domain_id;

    (void)dom_server_runtime_set_shard_version(runtime, 2u, 2u, 2u, 0u);
    (void)mmo_submit_intent(runtime, 1001u, 1u, domain_id, DOM_SERVER_INTENT_TRANSFER_OWNERSHIP, 0u, 2u, 8u, 10011u, 0);
    (void)dom_server_runtime_tick(runtime, 2);
    refusal_gap = mmo_count_refusals(runtime, DOM_SERVER_REFUSE_CAPABILITY_GAP);

    (void)dom_server_runtime_set_shard_state(runtime, 2u, DOM_SHARD_LIFECYCLE_DRAINING, 11u);
    (void)dom_server_runtime_set_shard_state(runtime, 2u, DOM_SHARD_LIFECYCLE_ACTIVE, 12u);
    (void)dom_server_runtime_set_shard_version(runtime, 2u, 3u, 1u, 0u);
    (void)mmo_submit_intent(runtime, 1001u, 1u, domain_id, DOM_SERVER_INTENT_TRANSFER_OWNERSHIP, 0u, 2u, 8u, 10012u, 3);
    (void)dom_server_runtime_tick(runtime, 4);

    owner_after = mmo_owner_for_domain(runtime, domain_id);
    refusal_state = mmo_count_refusals(runtime, DOM_SERVER_REFUSE_SHARD_STATE);

    printf("scenario=ops_shards workers=%u invariants=%s\n",
           (unsigned int)workers,
           "MMO2-LIFECYCLE-003,MMO2-ROLLING-004,MMO0-LOG-015");
    printf("ops.refusal_cap_gap=%u ops.refusal_shard_state=%u owner_after=%u lifecycle_count=%u checkpoints=%u\n",
           (unsigned int)refusal_gap,
           (unsigned int)refusal_state,
           (unsigned int)owner_after,
           (unsigned int)runtime->lifecycle_log.count,
           (unsigned int)runtime->checkpoints_taken);
    printf("shard.1 state=%s version=%u caps=%llu\n",
           dom_shard_lifecycle_state_name(runtime->shards[0].lifecycle_state),
           (unsigned int)runtime->shards[0].version_id,
           (unsigned long long)runtime->shards[0].capability_mask);
    printf("shard.2 state=%s version=%u caps=%llu baseline=%llu\n",
           dom_shard_lifecycle_state_name(runtime->shards[1].lifecycle_state),
           (unsigned int)runtime->shards[1].version_id,
           (unsigned long long)runtime->shards[1].capability_mask,
           (unsigned long long)runtime->shards[1].baseline_hash);

    free(runtime);
    return (refusal_gap > 0u && owner_after == 2u) ? 0 : 1;
}

static int mmo_run_ops_log(u32 workers)
{
    dom_server_runtime_config config;
    dom_server_runtime* runtime = 0;
    u64 domain_id = 0u;
    u32 message_before = 0u;
    u32 message_after = 0u;
    dom_shard_id owner_after = 0u;

    mmo_config_default(&config, 2u, workers);
    runtime = (dom_server_runtime*)calloc(1u, sizeof(*runtime));
    if (!runtime) {
        fprintf(stderr, "mmo: failed to allocate runtime\n");
        return 2;
    }
    if (dom_server_runtime_init(runtime, &config) != 0) {
        fprintf(stderr, "mmo: failed to init runtime\n");
        free(runtime);
        return 2;
    }
    (void)dom_server_runtime_add_client(runtime, 1101u, 1u, 0);
    domain_id = runtime->shards[0].domain_storage[0].domain_id;

    (void)mmo_submit_intent(runtime, 1101u, 1u, domain_id, DOM_SERVER_INTENT_TRANSFER_OWNERSHIP, 0u, 2u, 8u, 11011u, 0);
    (void)dom_server_runtime_tick(runtime, 0);
    message_before = runtime->message_log.message_count;
    if (message_before > 0u) {
        const dom_cross_shard_message* msg = &runtime->message_storage[0];
        printf("log.peek id=%llu origin=%u dest=%u delivery=%lld order=%llu\n",
               (unsigned long long)msg->message_id,
               (unsigned int)msg->origin_shard_id,
               (unsigned int)msg->dest_shard_id,
               (long long)msg->delivery_tick,
               (unsigned long long)msg->order_key);
    }

    (void)dom_server_runtime_tick(runtime, 1);
    message_after = runtime->message_log.message_count;
    owner_after = mmo_owner_for_domain(runtime, domain_id);

    printf("scenario=ops_log workers=%u invariants=%s\n",
           (unsigned int)workers,
           "MMO0-LOG-015,MMO2-LOG-006,MMO2-CHECKPOINT-001,SCALE0-DETERMINISM-004");
    printf("log.count_before=%u log.count_after=%u owner_after=%u message_applied=%llu\n",
           (unsigned int)message_before,
           (unsigned int)message_after,
           (unsigned int)owner_after,
           (unsigned long long)runtime->message_applied);

    free(runtime);
    return (message_before > 0u && message_after == 0u && owner_after == 2u) ? 0 : 1;
}

static void mmo_print_help(void)
{
    printf("mmo commands:\n");
    printf("  mmo two-node [--workers N]\n");
    printf("  mmo join-resync [--workers N]\n");
    printf("  mmo abuse [--workers N]\n");
    printf("  mmo legacy [--workers N]\n");
    printf("  mmo ops-checkpoint [--workers N]\n");
    printf("  mmo ops-recover [--workers N]\n");
    printf("  mmo ops-shards [--workers N]\n");
    printf("  mmo ops-log [--workers N]\n");
}

extern "C" int tools_run_mmo_cli(int argc, char** argv)
{
    const char* subcmd = 0;
    u32 workers = 1u;
    if (argc <= 0 || !argv) {
        mmo_print_help();
        return 0;
    }
    subcmd = argv[0];
    workers = mmo_parse_workers(argc, argv, 1u);

    if (strcmp(subcmd, "two-node") == 0 || strcmp(subcmd, "two_node") == 0) {
        return mmo_run_two_node(workers);
    }
    if (strcmp(subcmd, "join-resync") == 0 || strcmp(subcmd, "join_resync") == 0) {
        return mmo_run_join_resync(workers);
    }
    if (strcmp(subcmd, "abuse") == 0) {
        return mmo_run_abuse(workers);
    }
    if (strcmp(subcmd, "legacy") == 0) {
        return mmo_run_legacy(workers);
    }
    if (strcmp(subcmd, "ops-checkpoint") == 0 || strcmp(subcmd, "ops_checkpoint") == 0) {
        return mmo_run_ops_checkpoint(workers);
    }
    if (strcmp(subcmd, "ops-recover") == 0 || strcmp(subcmd, "ops_recover") == 0) {
        return mmo_run_ops_recover(workers);
    }
    if (strcmp(subcmd, "ops-shards") == 0 || strcmp(subcmd, "ops_shards") == 0) {
        return mmo_run_ops_shards(workers);
    }
    if (strcmp(subcmd, "ops-log") == 0 || strcmp(subcmd, "ops_log") == 0) {
        return mmo_run_ops_log(workers);
    }

    mmo_print_help();
    return 2;
}
