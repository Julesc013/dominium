/*
FILE: game/rules/scale/scale_collapse_expand.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale
RESPONSIBILITY: Deterministic collapse/expand entry points for SCALE-1 domains.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Collapse/expand results are stable across threads and replay.
*/
#include "dominium/rules/scale/scale_collapse_expand.h"

#include "domino/core/rng_model.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    DOM_SCALE_DETAIL_NONE = 0u,
    DOM_SCALE_DETAIL_COMMIT_TICK = 1u,
    DOM_SCALE_DETAIL_DOMAIN_UNSUPPORTED = 2u,
    DOM_SCALE_DETAIL_INTEREST_TIER2 = 3u,
    DOM_SCALE_DETAIL_BUDGET_COLLAPSE = 4u,
    DOM_SCALE_DETAIL_BUDGET_EXPAND = 5u,
    DOM_SCALE_DETAIL_TIER_CAP = 6u,
    DOM_SCALE_DETAIL_DWELL_TICKS = 7u,
    DOM_SCALE_DETAIL_CAPSULE_PARSE = 8u,
    DOM_SCALE_DETAIL_INVARIANT_MISMATCH = 9u,
    DOM_SCALE_DETAIL_CAPACITY = 10u,
    DOM_SCALE_DETAIL_MACRO_QUEUE_LIMIT = 11u,
    DOM_SCALE_DETAIL_BUDGET_MACRO_EVENT = 12u,
    DOM_SCALE_DETAIL_BUDGET_COMPACTION = 13u,
    DOM_SCALE_DETAIL_MACRO_SCHEDULE = 14u,
    DOM_SCALE_DETAIL_MACRO_EVENT = 15u,
    DOM_SCALE_DETAIL_MACRO_COMPACTION = 16u,
    DOM_SCALE_DETAIL_ACTIVE_DOMAIN_LIMIT = 17u,
    DOM_SCALE_DETAIL_BUDGET_REFINEMENT = 18u,
    DOM_SCALE_DETAIL_BUDGET_PLANNING = 19u,
    DOM_SCALE_DETAIL_BUDGET_SNAPSHOT = 20u,
    DOM_SCALE_DETAIL_DEFER_QUEUE_LIMIT = 21u
};

static const char* g_scale_rng_stream_agents_reconstruct =
    "noise.stream.scale.agents.reconstruct";
static const char* g_scale_rng_state_ext_agents_reconstruct =
    "rng.state.noise.stream.scale.agents.reconstruct";

static u64 dom_scale_fnv1a64_init(void)
{
    return 0xcbf29ce484222325ull;
}

static u64 dom_scale_fnv1a64_update(u64 hash, const unsigned char* bytes, size_t len)
{
    size_t i;
    if (!bytes) {
        return hash;
    }
    for (i = 0u; i < len; ++i) {
        hash ^= (u64)bytes[i];
        hash *= 0x100000001b3ull;
    }
    return hash;
}

static u64 dom_scale_hash_u32(u64 hash, u32 value)
{
    unsigned char bytes[4];
    bytes[0] = (unsigned char)((value >> 24) & 0xFFu);
    bytes[1] = (unsigned char)((value >> 16) & 0xFFu);
    bytes[2] = (unsigned char)((value >> 8) & 0xFFu);
    bytes[3] = (unsigned char)(value & 0xFFu);
    return dom_scale_fnv1a64_update(hash, bytes, sizeof(bytes));
}

static u64 dom_scale_hash_u64(u64 hash, u64 value)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((value >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((value >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((value >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((value >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((value >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((value >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((value >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(value & 0xFFu);
    return dom_scale_fnv1a64_update(hash, bytes, sizeof(bytes));
}

static u64 dom_scale_hash_i64(u64 hash, dom_act_time_t value)
{
    return dom_scale_hash_u64(hash, (u64)value);
}

static int dom_scale_parse_u64(const char* text, u64* out_value)
{
    const char* p;
    u64 value = 0u;
    if (!text || !out_value || *text == '\0') {
        return 0;
    }
    p = text;
    while (*p) {
        char c = *p++;
        if (c < '0' || c > '9') {
            return 0;
        }
        value = value * 10u + (u64)(c - '0');
    }
    *out_value = value;
    return 0;
}

static int dom_scale_parse_u32(const char* text, u32* out_value)
{
    u64 value = 0u;
    if (!dom_scale_parse_u64(text, &value)) {
        return 0;
    }
    *out_value = (u32)value;
    return 1;
}

static int dom_scale_parse_i64(const char* text, dom_act_time_t* out_value)
{
    const char* p;
    int neg = 0;
    u64 value = 0u;
    if (!text || !out_value) {
        return 0;
    }
    p = text;
    if (*p == '-') {
        neg = 1;
        ++p;
    }
    if (*p == '\0') {
        return 0;
    }
    while (*p) {
        char c = *p++;
        if (c < '0' || c > '9') {
            return 0;
        }
        value = value * 10u + (u64)(c - '0');
    }
    *out_value = neg ? (dom_act_time_t)(-(i64)value) : (dom_act_time_t)value;
    return 1;
}

static int dom_scale_parse_u64_strict(const char* text, u64* out_value)
{
    const char* p;
    u64 value = 0u;
    if (!text || !out_value || *text == '\0') {
        return 0;
    }
    p = text;
    while (*p) {
        char c = *p++;
        if (c < '0' || c > '9') {
            return 0;
        }
        value = value * 10u + (u64)(c - '0');
    }
    *out_value = value;
    return 1;
}

static u32 dom_scale_rng_state_from_seed(u32 base_seed, u64 domain_id, const char* stream_name)
{
    d_rng_state rng;
    u32 adjusted = base_seed;
    u32 domain_fold = d_rng_fold_u64(domain_id);
    u32 stream_hash = d_rng_hash_str32(stream_name);
    adjusted ^= domain_fold;
    adjusted ^= stream_hash;
    d_rng_state_from_context(&rng,
                             (u64)adjusted,
                             domain_id,
                             0u,
                             0u,
                             stream_name,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_STREAM);
    return rng.state;
}

static int dom_scale_is_tier2(dom_fidelity_tier tier)
{
    return tier >= DOM_FID_MICRO ? 1 : 0;
}

static int dom_scale_is_tier1(dom_fidelity_tier tier)
{
    return tier == DOM_FID_MESO ? 1 : 0;
}

static int dom_scale_resource_cmp(const dom_scale_resource_entry* a,
                                  const dom_scale_resource_entry* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->resource_id < b->resource_id) return -1;
    if (a->resource_id > b->resource_id) return 1;
    if (a->quantity < b->quantity) return -1;
    if (a->quantity > b->quantity) return 1;
    return 0;
}

static void dom_scale_resource_sort(dom_scale_resource_entry* entries, u32 count)
{
    u32 i;
    if (!entries) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_scale_resource_entry key = entries[i];
        u32 j = i;
        while (j > 0u && dom_scale_resource_cmp(&entries[j - 1u], &key) > 0) {
            entries[j] = entries[j - 1u];
            --j;
        }
        entries[j] = key;
    }
}

static int dom_scale_node_cmp(const dom_scale_network_node* a,
                              const dom_scale_network_node* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->node_id < b->node_id) return -1;
    if (a->node_id > b->node_id) return 1;
    if (a->node_kind < b->node_kind) return -1;
    if (a->node_kind > b->node_kind) return 1;
    return 0;
}

static void dom_scale_node_sort(dom_scale_network_node* nodes, u32 count)
{
    u32 i;
    if (!nodes) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_scale_network_node key = nodes[i];
        u32 j = i;
        while (j > 0u && dom_scale_node_cmp(&nodes[j - 1u], &key) > 0) {
            nodes[j] = nodes[j - 1u];
            --j;
        }
        nodes[j] = key;
    }
}

static int dom_scale_edge_cmp(const dom_scale_network_edge* a,
                              const dom_scale_network_edge* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->edge_id < b->edge_id) return -1;
    if (a->edge_id > b->edge_id) return 1;
    if (a->from_node_id < b->from_node_id) return -1;
    if (a->from_node_id > b->from_node_id) return 1;
    if (a->to_node_id < b->to_node_id) return -1;
    if (a->to_node_id > b->to_node_id) return 1;
    return 0;
}

static void dom_scale_edge_sort(dom_scale_network_edge* edges, u32 count)
{
    u32 i;
    if (!edges) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_scale_network_edge key = edges[i];
        u32 j = i;
        while (j > 0u && dom_scale_edge_cmp(&edges[j - 1u], &key) > 0) {
            edges[j] = edges[j - 1u];
            --j;
        }
        edges[j] = key;
    }
}

static int dom_scale_agent_cmp(const dom_scale_agent_entry* a,
                               const dom_scale_agent_entry* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->agent_id < b->agent_id) return -1;
    if (a->agent_id > b->agent_id) return 1;
    if (a->role_id < b->role_id) return -1;
    if (a->role_id > b->role_id) return 1;
    if (a->trait_mask < b->trait_mask) return -1;
    if (a->trait_mask > b->trait_mask) return 1;
    if (a->planning_bucket < b->planning_bucket) return -1;
    if (a->planning_bucket > b->planning_bucket) return 1;
    return 0;
}

static void dom_scale_agent_sort(dom_scale_agent_entry* agents, u32 count)
{
    u32 i;
    if (!agents) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_scale_agent_entry key = agents[i];
        u32 j = i;
        while (j > 0u && dom_scale_agent_cmp(&agents[j - 1u], &key) > 0) {
            agents[j] = agents[j - 1u];
            --j;
        }
        agents[j] = key;
    }
}

static void dom_scale_event_emit(dom_scale_event_log* log, const dom_scale_event* ev)
{
    if (!log || !ev || !log->events || log->capacity == 0u) {
        if (log) {
            log->overflow += 1u;
        }
        return;
    }
    if (log->count >= log->capacity) {
        log->overflow += 1u;
        return;
    }
    log->events[log->count++] = *ev;
}

void dom_scale_event_log_init(dom_scale_event_log* log,
                              dom_scale_event* storage,
                              u32 capacity)
{
    if (!log) {
        return;
    }
    log->events = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->overflow = 0u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_scale_event) * (size_t)capacity);
    }
}

void dom_scale_event_log_clear(dom_scale_event_log* log)
{
    if (!log) {
        return;
    }
    log->count = 0u;
    log->overflow = 0u;
    if (log->events && log->capacity > 0u) {
        memset(log->events, 0, sizeof(dom_scale_event) * (size_t)log->capacity);
    }
}

void dom_scale_budget_policy_default(dom_scale_budget_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
    policy->max_tier2_domains = 8u;
    policy->max_tier1_domains = 32u;
    policy->active_domain_budget = 0u;
    policy->refinement_budget_per_tick = 64u;
    policy->refinement_cost_units = 1u;
    policy->planning_budget_per_tick = 64u;
    policy->planning_cost_units = 1u;
    policy->collapse_budget_per_tick = 16u;
    policy->expand_budget_per_tick = 16u;
    policy->collapse_cost_units = 1u;
    policy->expand_cost_units = 1u;
    policy->macro_event_budget_per_tick = 64u;
    policy->macro_event_cost_units = 1u;
    policy->macro_queue_limit = 4096u;
    policy->compaction_budget_per_tick = 8u;
    policy->compaction_cost_units = 1u;
    policy->compaction_event_threshold = 256u;
    policy->compaction_time_threshold = 1024;
    policy->snapshot_budget_per_tick = 32u;
    policy->snapshot_cost_units = 1u;
    policy->deferred_queue_limit = 64u;
    policy->min_dwell_ticks = 4;
}

void dom_scale_interest_policy_default(dom_interest_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
    policy->enter_warm = DOM_INTEREST_STRENGTH_LOW;
    policy->exit_warm = DOM_INTEREST_STRENGTH_LOW / 2u;
    policy->enter_hot = DOM_INTEREST_STRENGTH_HIGH;
    policy->exit_hot = DOM_INTEREST_STRENGTH_MED;
    policy->min_dwell_ticks = 4;
}

void dom_scale_macro_policy_default(dom_scale_macro_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
    policy->macro_interval_ticks = 16;
    policy->macro_event_kind = 1u;
    policy->narrative_stride = 8u;
}

static void dom_scale_interest_state_configure(dom_interest_state* state,
                                               u64 domain_id,
                                               dom_act_time_t now_tick)
{
    if (!state) {
        return;
    }
    state->target_id = domain_id;
    state->target_kind = DOM_INTEREST_TARGET_REGION;
    state->state = DOM_REL_LATENT;
    state->last_change_tick = now_tick;
}

static void dom_scale_recount_active_tiers(dom_scale_context* ctx)
{
    u32 i;
    u32 tier1 = 0u;
    u32 tier2 = 0u;
    if (!ctx || !ctx->domains) {
        return;
    }
    for (i = 0u; i < ctx->domain_count; ++i) {
        dom_fidelity_tier tier = ctx->domains[i].tier;
        if (dom_scale_is_tier2(tier)) {
            tier2 += 1u;
        } else if (dom_scale_is_tier1(tier)) {
            tier1 += 1u;
        }
    }
    ctx->budget_state.active_tier1_domains = tier1;
    ctx->budget_state.active_tier2_domains = tier2;
}

static u32 dom_scale_find_domain_index(const dom_scale_context* ctx, u64 domain_id)
{
    u32 low = 0u;
    u32 high;
    if (!ctx || !ctx->domains || ctx->domain_count == 0u) {
        return 0xFFFFFFFFu;
    }
    high = ctx->domain_count;
    while (low < high) {
        u32 mid = low + (u32)((high - low) / 2u);
        u64 mid_id = ctx->domains[mid].domain_id;
        if (mid_id == domain_id) {
            return mid;
        }
        if (mid_id < domain_id) {
            low = mid + 1u;
        } else {
            high = mid;
        }
    }
    return 0xFFFFFFFFu;
}

void dom_scale_context_init(dom_scale_context* ctx,
                            d_world* world,
                            dom_scale_domain_slot* domain_storage,
                            u32 domain_capacity,
                            dom_interest_state* interest_storage,
                            u32 interest_capacity,
                            dom_scale_event_log* event_log,
                            dom_act_time_t now_tick,
                            u32 worker_count)
{
    if (!ctx) {
        return;
    }
    memset(ctx, 0, sizeof(*ctx));
    ctx->world = world;
    ctx->domains = domain_storage;
    ctx->domain_capacity = domain_capacity;
    ctx->domain_count = 0u;
    ctx->interest_states = interest_storage;
    ctx->interest_capacity = interest_capacity;
    ctx->event_log = event_log;
    ctx->now_tick = now_tick;
    ctx->worker_count = worker_count;
    dom_scale_budget_policy_default(&ctx->budget_policy);
    dom_scale_interest_policy_default(&ctx->interest_policy);
    memset(&ctx->budget_state, 0, sizeof(ctx->budget_state));
    if (domain_storage && domain_capacity > 0u) {
        memset(domain_storage, 0, sizeof(dom_scale_domain_slot) * (size_t)domain_capacity);
    }
    if (interest_storage && interest_capacity > 0u) {
        dom_interest_state_init(interest_storage, interest_capacity);
    }
}

int dom_scale_register_domain(dom_scale_context* ctx,
                              const dom_scale_domain_slot* slot)
{
    u32 i;
    u32 insert_at = 0u;
    if (!ctx || !slot || !ctx->domains || ctx->domain_capacity == 0u) {
        return -1;
    }
    if (ctx->domain_count >= ctx->domain_capacity) {
        return -2;
    }
    for (i = 0u; i < ctx->domain_count; ++i) {
        if (ctx->domains[i].domain_id == slot->domain_id) {
            return -3;
        }
        if (ctx->domains[i].domain_id > slot->domain_id) {
            insert_at = i;
            break;
        }
        insert_at = i + 1u;
    }
    for (i = ctx->domain_count; i > insert_at; --i) {
        ctx->domains[i] = ctx->domains[i - 1u];
        if (ctx->interest_states && i < ctx->interest_capacity) {
            ctx->interest_states[i] = ctx->interest_states[i - 1u];
        }
    }
    ctx->domains[insert_at] = *slot;
    ctx->domain_count += 1u;
    if (ctx->interest_states && insert_at < ctx->interest_capacity) {
        dom_scale_interest_state_configure(&ctx->interest_states[insert_at],
                                           slot->domain_id,
                                           ctx->now_tick);
    }
    dom_scale_recount_active_tiers(ctx);
    return 0;
}

dom_scale_domain_slot* dom_scale_find_domain(dom_scale_context* ctx,
                                             u64 domain_id)
{
    u32 index;
    if (!ctx || !ctx->domains) {
        return 0;
    }
    index = dom_scale_find_domain_index(ctx, domain_id);
    if (index == 0xFFFFFFFFu) {
        return 0;
    }
    return &ctx->domains[index];
}

static dom_interest_state* dom_scale_find_interest_state(dom_scale_context* ctx,
                                                         u64 domain_id)
{
    u32 index;
    if (!ctx || !ctx->interest_states) {
        return 0;
    }
    index = dom_scale_find_domain_index(ctx, domain_id);
    if (index == 0xFFFFFFFFu || index >= ctx->interest_capacity) {
        return 0;
    }
    if (ctx->interest_states[index].target_id != domain_id) {
        return 0;
    }
    return &ctx->interest_states[index];
}

static u64 dom_scale_commit_nonce(dom_act_time_t tick)
{
    u64 hash = dom_scale_fnv1a64_init();
    hash = dom_scale_hash_u64(hash, 0x5343414c452d3031ull);
    hash = dom_scale_hash_i64(hash, tick);
    return hash;
}

void dom_scale_commit_token_make(dom_scale_commit_token* token,
                                 dom_act_time_t commit_tick,
                                 u32 sequence)
{
    (void)sequence;
    if (!token) {
        return;
    }
    token->commit_tick = commit_tick;
    token->commit_nonce = dom_scale_commit_nonce(commit_tick);
}

int dom_scale_commit_token_validate(const dom_scale_commit_token* token,
                                    dom_act_time_t expected_tick)
{
    if (!token) {
        return 0;
    }
    if (token->commit_tick != expected_tick) {
        return 0;
    }
    return token->commit_nonce == dom_scale_commit_nonce(expected_tick) ? 1 : 0;
}

static u64 dom_scale_capsule_hash(const unsigned char* bytes, u32 byte_count)
{
    return dom_scale_fnv1a64_update(dom_scale_fnv1a64_init(), bytes, (size_t)byte_count);
}

static u64 dom_scale_capsule_id(u64 domain_id,
                                u32 domain_kind,
                                dom_act_time_t tick,
                                u32 reason_code)
{
    u64 hash = dom_scale_fnv1a64_init();
    hash = dom_scale_hash_u64(hash, domain_id);
    hash = dom_scale_hash_u32(hash, domain_kind);
    hash = dom_scale_hash_i64(hash, tick);
    hash = dom_scale_hash_u32(hash, reason_code);
    return hash;
}

static u32 dom_scale_seed_base(u64 capsule_id, dom_act_time_t tick)
{
    u64 mix = capsule_id ^ (u64)tick;
    mix ^= (mix >> 33);
    mix *= 0xff51afd7ed558ccdull;
    mix ^= (mix >> 33);
    return (u32)(mix & 0xFFFFFFFFu);
}

static int dom_scale_domain_supported(u32 domain_kind)
{
    if (domain_kind == DOM_SCALE_DOMAIN_RESOURCES ||
        domain_kind == DOM_SCALE_DOMAIN_NETWORK ||
        domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        return 1;
    }
    return 0;
}

static u32 dom_scale_policy_tier2_limit(const dom_scale_budget_policy* policy)
{
    if (!policy) {
        return 0u;
    }
    if (policy->active_domain_budget > 0u) {
        return policy->active_domain_budget;
    }
    return policy->max_tier2_domains;
}

static u32 dom_scale_policy_deferred_limit(const dom_scale_budget_policy* policy)
{
    u32 limit = policy ? policy->deferred_queue_limit : 0u;
    if (limit > DOM_SCALE_DEFER_QUEUE_CAP) {
        return DOM_SCALE_DEFER_QUEUE_CAP;
    }
    return limit;
}

static void dom_scale_budget_begin_tick(dom_scale_context* ctx, dom_act_time_t tick)
{
    if (!ctx) {
        return;
    }
    if (ctx->budget_state.budget_tick == tick) {
        return;
    }
    ctx->budget_state.budget_tick = tick;
    ctx->budget_state.refinement_used = 0u;
    ctx->budget_state.planning_used = 0u;
    ctx->budget_state.collapse_used = 0u;
    ctx->budget_state.expand_used = 0u;
    ctx->budget_state.macro_event_used = 0u;
    ctx->budget_state.compaction_used = 0u;
    ctx->budget_state.snapshot_used = 0u;
}

static int dom_scale_budget_allows_collapse(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return 0;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->collapse_cost_units ? policy->collapse_cost_units : 1u;
    if (policy->collapse_budget_per_tick == 0u) {
        return 1;
    }
    return ctx->budget_state.collapse_used + cost <= policy->collapse_budget_per_tick ? 1 : 0;
}

static int dom_scale_budget_allows_expand(dom_scale_context* ctx,
                                          dom_fidelity_tier target_tier,
                                          u32* out_detail_code)
{
    const dom_scale_budget_policy* policy;
    u32 refine_cost;
    u32 expand_cost;
    u32 tier2_limit;
    if (out_detail_code) {
        *out_detail_code = DOM_SCALE_DETAIL_NONE;
    }
    if (!ctx) {
        return 0;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    refine_cost = policy->refinement_cost_units ? policy->refinement_cost_units : 1u;
    expand_cost = policy->expand_cost_units ? policy->expand_cost_units : 1u;
    if (policy->refinement_budget_per_tick > 0u &&
        ctx->budget_state.refinement_used + refine_cost > policy->refinement_budget_per_tick) {
        if (out_detail_code) {
            *out_detail_code = DOM_SCALE_DETAIL_BUDGET_REFINEMENT;
        }
        return 0;
    }
    if (policy->expand_budget_per_tick > 0u &&
        ctx->budget_state.expand_used + expand_cost > policy->expand_budget_per_tick) {
        if (out_detail_code) {
            *out_detail_code = DOM_SCALE_DETAIL_BUDGET_EXPAND;
        }
        return 0;
    }
    tier2_limit = dom_scale_policy_tier2_limit(policy);
    if (dom_scale_is_tier2(target_tier) &&
        tier2_limit > 0u &&
        ctx->budget_state.active_tier2_domains >= tier2_limit) {
        if (out_detail_code) {
            *out_detail_code = DOM_SCALE_DETAIL_ACTIVE_DOMAIN_LIMIT;
        }
        return 0;
    }
    if (dom_scale_is_tier1(target_tier) &&
        policy->max_tier1_domains > 0u &&
        ctx->budget_state.active_tier1_domains >= policy->max_tier1_domains) {
        if (out_detail_code) {
            *out_detail_code = DOM_SCALE_DETAIL_TIER_CAP;
        }
        return 0;
    }
    return 1;
}

static int dom_scale_budget_allows_planning(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return 0;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->planning_cost_units ? policy->planning_cost_units : 1u;
    if (policy->planning_budget_per_tick == 0u) {
        return 1;
    }
    return ctx->budget_state.planning_used + cost <= policy->planning_budget_per_tick ? 1 : 0;
}

static int dom_scale_budget_allows_snapshot(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return 0;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->snapshot_cost_units ? policy->snapshot_cost_units : 1u;
    if (policy->snapshot_budget_per_tick == 0u) {
        return 1;
    }
    return ctx->budget_state.snapshot_used + cost <= policy->snapshot_budget_per_tick ? 1 : 0;
}

static int dom_scale_budget_allows_macro_event(dom_scale_context* ctx, dom_act_time_t event_tick)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return 0;
    }
    (void)event_tick;
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->macro_event_cost_units ? policy->macro_event_cost_units : 1u;
    if (policy->macro_event_budget_per_tick == 0u) {
        return 1;
    }
    return ctx->budget_state.macro_event_used + cost <= policy->macro_event_budget_per_tick ? 1 : 0;
}

static int dom_scale_budget_allows_compaction(dom_scale_context* ctx, dom_act_time_t compact_tick)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return 0;
    }
    (void)compact_tick;
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->compaction_cost_units ? policy->compaction_cost_units : 1u;
    if (policy->compaction_budget_per_tick == 0u) {
        return 1;
    }
    return ctx->budget_state.compaction_used + cost <= policy->compaction_budget_per_tick ? 1 : 0;
}

static int dom_scale_macro_queue_within_limit(dom_scale_context* ctx, u32* out_detail_code)
{
    const dom_scale_budget_policy* policy;
    u32 limit;
    if (out_detail_code) {
        *out_detail_code = DOM_SCALE_DETAIL_NONE;
    }
    if (!ctx || !ctx->world) {
        return 0;
    }
    policy = &ctx->budget_policy;
    limit = policy->macro_queue_limit;
    if (limit == 0u) {
        return 1;
    }
    if (dom_macro_event_queue_count(ctx->world) >= limit) {
        if (out_detail_code) {
            *out_detail_code = DOM_SCALE_DETAIL_MACRO_QUEUE_LIMIT;
        }
        return 0;
    }
    return 1;
}

static void dom_scale_budget_consume_collapse(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->collapse_cost_units ? policy->collapse_cost_units : 1u;
    ctx->budget_state.collapse_used += cost;
}

static void dom_scale_budget_consume_expand(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->expand_cost_units ? policy->expand_cost_units : 1u;
    ctx->budget_state.expand_used += cost;
}

static void dom_scale_budget_consume_refinement(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->refinement_cost_units ? policy->refinement_cost_units : 1u;
    ctx->budget_state.refinement_used += cost;
}

static void dom_scale_budget_consume_planning(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->planning_cost_units ? policy->planning_cost_units : 1u;
    ctx->budget_state.planning_used += cost;
}

static void dom_scale_budget_consume_snapshot(dom_scale_context* ctx)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->snapshot_cost_units ? policy->snapshot_cost_units : 1u;
    ctx->budget_state.snapshot_used += cost;
}

static void dom_scale_budget_consume_macro_event(dom_scale_context* ctx, dom_act_time_t event_tick)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return;
    }
    (void)event_tick;
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->macro_event_cost_units ? policy->macro_event_cost_units : 1u;
    ctx->budget_state.macro_event_used += cost;
}

static void dom_scale_budget_consume_compaction(dom_scale_context* ctx, dom_act_time_t compact_tick)
{
    const dom_scale_budget_policy* policy;
    u32 cost;
    if (!ctx) {
        return;
    }
    (void)compact_tick;
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    cost = policy->compaction_cost_units ? policy->compaction_cost_units : 1u;
    ctx->budget_state.compaction_used += cost;
}

static int dom_scale_dwell_elapsed(dom_act_time_t now_tick,
                                   dom_act_time_t last_tick,
                                   dom_act_time_t min_dwell_ticks)
{
    dom_act_time_t elapsed;
    if (min_dwell_ticks <= 0) {
        return 1;
    }
    elapsed = now_tick - last_tick;
    if (elapsed < 0) {
        elapsed = 0;
    }
    return elapsed >= min_dwell_ticks ? 1 : 0;
}

static void dom_scale_budget_adjust_for_transition(dom_scale_context* ctx,
                                                   dom_fidelity_tier from_tier,
                                                   dom_fidelity_tier to_tier)
{
    if (!ctx) {
        return;
    }
    if (dom_scale_is_tier2(from_tier) && ctx->budget_state.active_tier2_domains > 0u) {
        ctx->budget_state.active_tier2_domains -= 1u;
    } else if (dom_scale_is_tier1(from_tier) && ctx->budget_state.active_tier1_domains > 0u) {
        ctx->budget_state.active_tier1_domains -= 1u;
    }
    if (dom_scale_is_tier2(to_tier)) {
        ctx->budget_state.active_tier2_domains += 1u;
    } else if (dom_scale_is_tier1(to_tier)) {
        ctx->budget_state.active_tier1_domains += 1u;
    }
}

static void dom_scale_result_init(dom_scale_operation_result* result,
                                  u64 domain_id,
                                  u32 domain_kind,
                                  dom_act_time_t tick)
{
    if (!result) {
        return;
    }
    memset(result, 0, sizeof(*result));
    result->domain_id = domain_id;
    result->domain_kind = domain_kind;
    result->tick = tick;
    result->from_tier = DOM_FID_LATENT;
    result->to_tier = DOM_FID_LATENT;
}

static int dom_scale_deferred_cmp(const dom_scale_deferred_op* a,
                                  const dom_scale_deferred_op* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->domain_id < b->domain_id) return -1;
    if (a->domain_id > b->domain_id) return 1;
    if (a->capsule_id < b->capsule_id) return -1;
    if (a->capsule_id > b->capsule_id) return 1;
    if (a->kind < b->kind) return -1;
    if (a->kind > b->kind) return 1;
    if (a->requested_tick < b->requested_tick) return -1;
    if (a->requested_tick > b->requested_tick) return 1;
    if (a->reason_code < b->reason_code) return -1;
    if (a->reason_code > b->reason_code) return 1;
    if (a->budget_kind < b->budget_kind) return -1;
    if (a->budget_kind > b->budget_kind) return 1;
    return 0;
}

static int dom_scale_deferred_enqueue(dom_scale_context* ctx,
                                      const dom_scale_deferred_op* op)
{
    u32 limit;
    u32 i;
    if (!ctx || !op) {
        return 0;
    }
    limit = dom_scale_policy_deferred_limit(&ctx->budget_policy);
    for (i = 0u; i < ctx->budget_state.deferred_count; ++i) {
        if (dom_scale_deferred_cmp(&ctx->budget_state.deferred_ops[i], op) == 0) {
            return 1;
        }
    }
    if (ctx->budget_state.deferred_count >= limit ||
        ctx->budget_state.deferred_count >= DOM_SCALE_DEFER_QUEUE_CAP) {
        ctx->budget_state.deferred_overflow += 1u;
        return 0;
    }
    i = ctx->budget_state.deferred_count;
    while (i > 0u && dom_scale_deferred_cmp(&ctx->budget_state.deferred_ops[i - 1u], op) > 0) {
        ctx->budget_state.deferred_ops[i] = ctx->budget_state.deferred_ops[i - 1u];
        --i;
    }
    ctx->budget_state.deferred_ops[i] = *op;
    ctx->budget_state.deferred_count += 1u;
    return 1;
}

static void dom_scale_deferred_remove_domain(dom_scale_context* ctx, u64 domain_id)
{
    u32 i = 0u;
    if (!ctx) {
        return;
    }
    while (i < ctx->budget_state.deferred_count) {
        if (ctx->budget_state.deferred_ops[i].domain_id == domain_id) {
            u32 j;
            for (j = i + 1u; j < ctx->budget_state.deferred_count; ++j) {
                ctx->budget_state.deferred_ops[j - 1u] = ctx->budget_state.deferred_ops[j];
            }
            ctx->budget_state.deferred_count -= 1u;
            memset(&ctx->budget_state.deferred_ops[ctx->budget_state.deferred_count],
                   0,
                   sizeof(ctx->budget_state.deferred_ops[0]));
            continue;
        }
        ++i;
    }
}

static void dom_scale_deferred_remove_kind(dom_scale_context* ctx, u64 domain_id, u32 kind)
{
    u32 i = 0u;
    if (!ctx) {
        return;
    }
    while (i < ctx->budget_state.deferred_count) {
        if (ctx->budget_state.deferred_ops[i].domain_id == domain_id &&
            ctx->budget_state.deferred_ops[i].kind == kind) {
            u32 j;
            for (j = i + 1u; j < ctx->budget_state.deferred_count; ++j) {
                ctx->budget_state.deferred_ops[j - 1u] = ctx->budget_state.deferred_ops[j];
            }
            ctx->budget_state.deferred_count -= 1u;
            memset(&ctx->budget_state.deferred_ops[ctx->budget_state.deferred_count],
                   0,
                   sizeof(ctx->budget_state.deferred_ops[0]));
            continue;
        }
        ++i;
    }
}

static void dom_scale_deferred_remove_match(dom_scale_context* ctx,
                                            u64 domain_id,
                                            u32 kind,
                                            u32 reason_code)
{
    u32 i = 0u;
    if (!ctx) {
        return;
    }
    while (i < ctx->budget_state.deferred_count) {
        dom_scale_deferred_op* op = &ctx->budget_state.deferred_ops[i];
        if (op->domain_id == domain_id &&
            op->kind == kind &&
            (reason_code == 0u || op->reason_code == reason_code)) {
            u32 j;
            for (j = i + 1u; j < ctx->budget_state.deferred_count; ++j) {
                ctx->budget_state.deferred_ops[j - 1u] = ctx->budget_state.deferred_ops[j];
            }
            ctx->budget_state.deferred_count -= 1u;
            memset(&ctx->budget_state.deferred_ops[ctx->budget_state.deferred_count],
                   0,
                   sizeof(ctx->budget_state.deferred_ops[0]));
            continue;
        }
        ++i;
    }
}

static u32 dom_scale_budget_kind_from_detail(u32 detail_code)
{
    switch (detail_code) {
    case DOM_SCALE_DETAIL_ACTIVE_DOMAIN_LIMIT:
    case DOM_SCALE_DETAIL_TIER_CAP:
        return DOM_SCALE_BUDGET_ACTIVE_DOMAIN;
    case DOM_SCALE_DETAIL_BUDGET_REFINEMENT:
    case DOM_SCALE_DETAIL_BUDGET_EXPAND:
        return DOM_SCALE_BUDGET_REFINEMENT;
    case DOM_SCALE_DETAIL_BUDGET_COLLAPSE:
    case DOM_SCALE_DETAIL_BUDGET_COMPACTION:
        return DOM_SCALE_BUDGET_COLLAPSE;
    case DOM_SCALE_DETAIL_BUDGET_MACRO_EVENT:
    case DOM_SCALE_DETAIL_MACRO_QUEUE_LIMIT:
    case DOM_SCALE_DETAIL_MACRO_SCHEDULE:
        return DOM_SCALE_BUDGET_MACRO_EVENT;
    case DOM_SCALE_DETAIL_BUDGET_PLANNING:
        return DOM_SCALE_BUDGET_AGENT_PLANNING;
    case DOM_SCALE_DETAIL_BUDGET_SNAPSHOT:
        return DOM_SCALE_BUDGET_SNAPSHOT;
    case DOM_SCALE_DETAIL_DEFER_QUEUE_LIMIT:
        return DOM_SCALE_BUDGET_DEFER_QUEUE;
    default:
        break;
    }
    return DOM_SCALE_BUDGET_NONE;
}

static u32 dom_scale_budget_refusal_code(u32 budget_kind, u32 detail_code)
{
    (void)detail_code;
    switch (budget_kind) {
    case DOM_SCALE_BUDGET_ACTIVE_DOMAIN:
        return DOM_SCALE_REFUSE_ACTIVE_DOMAIN_LIMIT;
    case DOM_SCALE_BUDGET_REFINEMENT:
        return DOM_SCALE_REFUSE_REFINEMENT_BUDGET;
    case DOM_SCALE_BUDGET_MACRO_EVENT:
        return DOM_SCALE_REFUSE_MACRO_EVENT_BUDGET;
    case DOM_SCALE_BUDGET_AGENT_PLANNING:
        return DOM_SCALE_REFUSE_AGENT_PLANNING_BUDGET;
    case DOM_SCALE_BUDGET_SNAPSHOT:
        return DOM_SCALE_REFUSE_SNAPSHOT_BUDGET;
    case DOM_SCALE_BUDGET_COLLAPSE:
        return DOM_SCALE_REFUSE_COLLAPSE_BUDGET;
    case DOM_SCALE_BUDGET_DEFER_QUEUE:
        return DOM_SCALE_REFUSE_DEFER_QUEUE_LIMIT;
    default:
        break;
    }
    return DOM_SCALE_REFUSE_BUDGET_EXCEEDED;
}

static void dom_scale_budget_record_refusal(dom_scale_context* ctx, u32 budget_kind)
{
    if (!ctx) {
        return;
    }
    switch (budget_kind) {
    case DOM_SCALE_BUDGET_ACTIVE_DOMAIN:
        ctx->budget_state.refusal_active_domain_limit += 1u;
        break;
    case DOM_SCALE_BUDGET_REFINEMENT:
        ctx->budget_state.refusal_refinement_budget += 1u;
        break;
    case DOM_SCALE_BUDGET_MACRO_EVENT:
        ctx->budget_state.refusal_macro_event_budget += 1u;
        break;
    case DOM_SCALE_BUDGET_AGENT_PLANNING:
        ctx->budget_state.refusal_agent_planning_budget += 1u;
        break;
    case DOM_SCALE_BUDGET_SNAPSHOT:
        ctx->budget_state.refusal_snapshot_budget += 1u;
        break;
    case DOM_SCALE_BUDGET_COLLAPSE:
        ctx->budget_state.refusal_collapse_budget += 1u;
        break;
    case DOM_SCALE_BUDGET_DEFER_QUEUE:
        ctx->budget_state.refusal_defer_queue_limit += 1u;
        break;
    default:
        break;
    }
}

static void dom_scale_budget_fill_event(dom_scale_context* ctx,
                                        dom_scale_event* ev,
                                        u32 detail_code)
{
    const dom_scale_budget_policy* policy;
    u32 budget_kind;
    if (!ctx || !ev) {
        return;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    policy = &ctx->budget_policy;
    budget_kind = dom_scale_budget_kind_from_detail(detail_code);
    ev->budget_kind = budget_kind;
    ev->budget_queue = ctx->budget_state.deferred_count;
    ev->budget_overflow = ctx->budget_state.deferred_overflow;
    switch (budget_kind) {
    case DOM_SCALE_BUDGET_ACTIVE_DOMAIN:
        ev->budget_limit = dom_scale_policy_tier2_limit(policy);
        ev->budget_used = ctx->budget_state.active_tier2_domains;
        ev->budget_cost = 1u;
        break;
    case DOM_SCALE_BUDGET_REFINEMENT:
        if (detail_code == DOM_SCALE_DETAIL_BUDGET_EXPAND) {
            ev->budget_limit = policy->expand_budget_per_tick;
            ev->budget_used = ctx->budget_state.expand_used;
            ev->budget_cost = policy->expand_cost_units ? policy->expand_cost_units : 1u;
        } else {
            ev->budget_limit = policy->refinement_budget_per_tick;
            ev->budget_used = ctx->budget_state.refinement_used;
            ev->budget_cost = policy->refinement_cost_units ? policy->refinement_cost_units : 1u;
        }
        break;
    case DOM_SCALE_BUDGET_COLLAPSE:
        ev->budget_limit = policy->collapse_budget_per_tick;
        ev->budget_used = ctx->budget_state.collapse_used;
        ev->budget_cost = policy->collapse_cost_units ? policy->collapse_cost_units : 1u;
        break;
    case DOM_SCALE_BUDGET_MACRO_EVENT:
        if (detail_code == DOM_SCALE_DETAIL_MACRO_QUEUE_LIMIT && ctx->world) {
            ev->budget_limit = policy->macro_queue_limit;
            ev->budget_used = dom_macro_event_queue_count(ctx->world);
            ev->budget_cost = 1u;
        } else {
            ev->budget_limit = policy->macro_event_budget_per_tick;
            ev->budget_used = ctx->budget_state.macro_event_used;
            ev->budget_cost = policy->macro_event_cost_units ? policy->macro_event_cost_units : 1u;
        }
        break;
    case DOM_SCALE_BUDGET_AGENT_PLANNING:
        ev->budget_limit = policy->planning_budget_per_tick;
        ev->budget_used = ctx->budget_state.planning_used;
        ev->budget_cost = policy->planning_cost_units ? policy->planning_cost_units : 1u;
        break;
    case DOM_SCALE_BUDGET_SNAPSHOT:
        ev->budget_limit = policy->snapshot_budget_per_tick;
        ev->budget_used = ctx->budget_state.snapshot_used;
        ev->budget_cost = policy->snapshot_cost_units ? policy->snapshot_cost_units : 1u;
        break;
    case DOM_SCALE_BUDGET_DEFER_QUEUE:
        ev->budget_limit = dom_scale_policy_deferred_limit(policy);
        ev->budget_used = ctx->budget_state.deferred_count;
        ev->budget_cost = 1u;
        break;
    default:
        ev->budget_limit = 0u;
        ev->budget_used = 0u;
        ev->budget_cost = 0u;
        break;
    }
}

static void dom_scale_emit_refusal(dom_scale_context* ctx,
                                   u64 domain_id,
                                   u32 domain_kind,
                                   u32 reason_code,
                                   u32 refusal_code,
                                   u32 detail_code,
                                   dom_scale_operation_result* out_result)
{
    dom_scale_event ev;
    if (out_result) {
        out_result->refusal_code = refusal_code;
    }
    if (!ctx || !ctx->event_log) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.kind = DOM_SCALE_EVENT_REFUSAL;
    ev.domain_id = domain_id;
    ev.domain_kind = domain_kind;
    ev.reason_code = reason_code;
    ev.refusal_code = refusal_code;
    ev.defer_code = DOM_SCALE_DEFER_NONE;
    ev.detail_code = detail_code;
    ev.tick = ctx->now_tick;
    dom_scale_budget_fill_event(ctx, &ev, detail_code);
    dom_scale_budget_record_refusal(ctx, ev.budget_kind);
    dom_scale_event_emit(ctx->event_log, &ev);
}

static void dom_scale_emit_defer(dom_scale_context* ctx,
                                 u64 domain_id,
                                 u32 domain_kind,
                                 u32 reason_code,
                                 u32 defer_code,
                                 u32 detail_code,
                                 dom_scale_operation_result* out_result)
{
    dom_scale_event ev;
    if (out_result) {
        out_result->defer_code = defer_code;
    }
    if (!ctx || !ctx->event_log) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.kind = DOM_SCALE_EVENT_DEFER;
    ev.domain_id = domain_id;
    ev.domain_kind = domain_kind;
    ev.reason_code = reason_code;
    ev.refusal_code = DOM_SCALE_REFUSE_NONE;
    ev.defer_code = defer_code;
    ev.detail_code = detail_code;
    ev.tick = ctx->now_tick;
    dom_scale_budget_fill_event(ctx, &ev, detail_code);
    dom_scale_event_emit(ctx->event_log, &ev);
}

static int dom_scale_enqueue_defer(dom_scale_context* ctx,
                                   u64 domain_id,
                                   u32 domain_kind,
                                   u64 capsule_id,
                                   dom_fidelity_tier target_tier,
                                   u32 reason_code,
                                   u32 defer_code,
                                   u32 detail_code,
                                   u32 deferred_kind,
                                   u32 budget_kind,
                                   dom_scale_operation_result* out_result)
{
    dom_scale_deferred_op op;
    u32 deferred_limit;
    if (!ctx) {
        return 0;
    }
    deferred_limit = dom_scale_policy_deferred_limit(&ctx->budget_policy);
    if (deferred_limit == 0u) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               domain_kind,
                               reason_code,
                               dom_scale_budget_refusal_code(budget_kind, detail_code),
                               detail_code,
                               out_result);
        return 0;
    }
    memset(&op, 0, sizeof(op));
    op.kind = deferred_kind;
    op.budget_kind = budget_kind;
    op.domain_id = domain_id;
    op.capsule_id = capsule_id;
    op.target_tier = target_tier;
    op.requested_tick = ctx->now_tick;
    op.reason_code = reason_code;
    if (!dom_scale_deferred_enqueue(ctx, &op)) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               domain_kind,
                               reason_code,
                               DOM_SCALE_REFUSE_DEFER_QUEUE_LIMIT,
                               DOM_SCALE_DETAIL_DEFER_QUEUE_LIMIT,
                               out_result);
        return 0;
    }
    dom_scale_emit_defer(ctx,
                         domain_id,
                         domain_kind,
                         reason_code,
                         defer_code,
                         detail_code,
                         out_result);
    return 1;
}

static void dom_scale_emit_collapse(dom_scale_context* ctx,
                                    u64 domain_id,
                                    u32 domain_kind,
                                    u64 capsule_id,
                                    u32 reason_code,
                                    u32 seed_value)
{
    dom_scale_event ev;
    if (!ctx || !ctx->event_log) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.kind = DOM_SCALE_EVENT_COLLAPSE;
    ev.domain_id = domain_id;
    ev.domain_kind = domain_kind;
    ev.capsule_id = capsule_id;
    ev.reason_code = reason_code;
    ev.seed_value = seed_value;
    ev.tick = ctx->now_tick;
    dom_scale_event_emit(ctx->event_log, &ev);
}

static void dom_scale_emit_expand(dom_scale_context* ctx,
                                  u64 domain_id,
                                  u32 domain_kind,
                                  u64 capsule_id,
                                  u32 reason_code,
                                  u32 seed_value)
{
    dom_scale_event ev;
    if (!ctx || !ctx->event_log) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.kind = DOM_SCALE_EVENT_EXPAND;
    ev.domain_id = domain_id;
    ev.domain_kind = domain_kind;
    ev.capsule_id = capsule_id;
    ev.reason_code = reason_code;
    ev.seed_value = seed_value;
    ev.tick = ctx->now_tick;
    dom_scale_event_emit(ctx->event_log, &ev);
}

static void dom_scale_emit_macro_schedule(dom_scale_context* ctx,
                                          u64 domain_id,
                                          u32 domain_kind,
                                          u64 capsule_id,
                                          u32 reason_code,
                                          u32 seed_value,
                                          u32 detail_code)
{
    dom_scale_event ev;
    if (!ctx || !ctx->event_log) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.kind = DOM_SCALE_EVENT_MACRO_SCHEDULE;
    ev.domain_id = domain_id;
    ev.domain_kind = domain_kind;
    ev.capsule_id = capsule_id;
    ev.reason_code = reason_code;
    ev.seed_value = seed_value;
    ev.detail_code = detail_code;
    ev.tick = ctx->now_tick;
    dom_scale_event_emit(ctx->event_log, &ev);
}

static void dom_scale_emit_macro_execute(dom_scale_context* ctx,
                                         u64 domain_id,
                                         u32 domain_kind,
                                         u64 capsule_id,
                                         dom_act_time_t event_tick,
                                         u32 seed_value,
                                         u32 detail_code)
{
    dom_scale_event ev;
    if (!ctx || !ctx->event_log) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.kind = DOM_SCALE_EVENT_MACRO_EXECUTE;
    ev.domain_id = domain_id;
    ev.domain_kind = domain_kind;
    ev.capsule_id = capsule_id;
    ev.seed_value = seed_value;
    ev.detail_code = detail_code;
    ev.tick = event_tick;
    dom_scale_event_emit(ctx->event_log, &ev);
}

static void dom_scale_emit_macro_compact(dom_scale_context* ctx,
                                         u64 domain_id,
                                         u32 domain_kind,
                                         u64 capsule_id,
                                         dom_act_time_t compact_tick,
                                         u32 seed_value,
                                         u32 detail_code)
{
    dom_scale_event ev;
    if (!ctx || !ctx->event_log) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.kind = DOM_SCALE_EVENT_MACRO_COMPACT;
    ev.domain_id = domain_id;
    ev.domain_kind = domain_kind;
    ev.capsule_id = capsule_id;
    ev.seed_value = seed_value;
    ev.detail_code = detail_code;
    ev.tick = compact_tick;
    dom_scale_event_emit(ctx->event_log, &ev);
}

static int dom_scale_expand_apply(dom_scale_context* ctx,
                                  dom_scale_domain_slot* slot,
                                  dom_scale_capsule_data data,
                                  dom_fidelity_tier from_tier,
                                  dom_fidelity_tier to_tier,
                                  u32 expand_reason,
                                  u64 capsule_id,
                                  u64 capsule_hash,
                                  dom_scale_operation_result* out_result);

typedef struct dom_scale_role_trait_bucket {
    u32 role_id;
    u32 trait_mask;
    u32 count;
} dom_scale_role_trait_bucket;

typedef struct dom_scale_planning_bucket {
    u32 planning_bucket;
    u32 count;
} dom_scale_planning_bucket;

static void dom_scale_resource_buckets(const dom_scale_resource_entry* entries,
                                       u32 count,
                                       u64* out_bucket0,
                                       u64* out_bucket1,
                                       u64* out_bucket2,
                                       u64* out_bucket3,
                                       u64* out_total_qty)
{
    u32 i;
    u64 b0 = 0u;
    u64 b1 = 0u;
    u64 b2 = 0u;
    u64 b3 = 0u;
    u64 total = 0u;
    for (i = 0u; i < count; ++i) {
        u64 qty = entries[i].quantity;
        total += qty;
        if (qty < 10u) {
            b0 += 1u;
        } else if (qty < 100u) {
            b1 += 1u;
        } else if (qty < 1000u) {
            b2 += 1u;
        } else {
            b3 += 1u;
        }
    }
    if (out_bucket0) *out_bucket0 = b0;
    if (out_bucket1) *out_bucket1 = b1;
    if (out_bucket2) *out_bucket2 = b2;
    if (out_bucket3) *out_bucket3 = b3;
    if (out_total_qty) *out_total_qty = total;
}

static void dom_scale_wear_distribution(const dom_scale_network_edge* edges,
                                        u32 edge_count,
                                        u32* out_b0,
                                        u32* out_b1,
                                        u32* out_b2,
                                        u32* out_b3,
                                        u32* out_mean,
                                        u32* out_p95)
{
    u64 b0 = 0u;
    u64 b1 = 0u;
    u64 b2 = 0u;
    u64 b3 = 0u;
    u64 total = 0u;
    u64 weighted = 0u;
    u64 target = 0u;
    u64 accum = 0u;
    u32 mean = 0u;
    u32 p95 = 0u;
    u32 i;
    for (i = 0u; i < edge_count; ++i) {
        b0 += edges[i].wear_bucket0;
        b1 += edges[i].wear_bucket1;
        b2 += edges[i].wear_bucket2;
        b3 += edges[i].wear_bucket3;
    }
    total = b0 + b1 + b2 + b3;
    weighted = (0u * b0) + (1u * b1) + (2u * b2) + (3u * b3);
    if (total > 0u) {
        mean = (u32)(weighted / total);
        target = (total * 95u + 99u) / 100u;
        accum = b0;
        if (accum >= target) {
            p95 = 0u;
        } else {
            accum += b1;
            if (accum >= target) {
                p95 = 1u;
            } else {
                accum += b2;
                p95 = (accum >= target) ? 2u : 3u;
            }
        }
    }
    if (out_b0) *out_b0 = (u32)b0;
    if (out_b1) *out_b1 = (u32)b1;
    if (out_b2) *out_b2 = (u32)b2;
    if (out_b3) *out_b3 = (u32)b3;
    if (out_mean) *out_mean = mean;
    if (out_p95) *out_p95 = p95;
}

static u32 dom_scale_bucket_insert_role_trait(dom_scale_role_trait_bucket* buckets,
                                              u32 count,
                                              u32 capacity,
                                              u32 role_id,
                                              u32 trait_mask)
{
    u32 i;
    if (!buckets || capacity == 0u) {
        return count;
    }
    for (i = 0u; i < count; ++i) {
        if (buckets[i].role_id == role_id && buckets[i].trait_mask == trait_mask) {
            buckets[i].count += 1u;
            return count;
        }
        if (buckets[i].role_id > role_id ||
            (buckets[i].role_id == role_id && buckets[i].trait_mask > trait_mask)) {
            break;
        }
    }
    if (count >= capacity) {
        return count;
    }
    {
        u32 j;
        for (j = count; j > i; --j) {
            buckets[j] = buckets[j - 1u];
        }
        buckets[i].role_id = role_id;
        buckets[i].trait_mask = trait_mask;
        buckets[i].count = 1u;
    }
    return count + 1u;
}

static u32 dom_scale_bucket_insert_planning(dom_scale_planning_bucket* buckets,
                                            u32 count,
                                            u32 capacity,
                                            u32 planning_bucket)
{
    u32 i;
    if (!buckets || capacity == 0u) {
        return count;
    }
    for (i = 0u; i < count; ++i) {
        if (buckets[i].planning_bucket == planning_bucket) {
            buckets[i].count += 1u;
            return count;
        }
        if (buckets[i].planning_bucket > planning_bucket) {
            break;
        }
    }
    if (count >= capacity) {
        return count;
    }
    {
        u32 j;
        for (j = count; j > i; --j) {
            buckets[j] = buckets[j - 1u];
        }
        buckets[i].planning_bucket = planning_bucket;
        buckets[i].count = 1u;
    }
    return count + 1u;
}

static u64 dom_scale_resource_invariant_hash(const dom_scale_resource_entry* entries,
                                             u32 count,
                                             dom_act_time_t now_tick)
{
    u64 hash = dom_scale_fnv1a64_init();
    u32 i;
    hash = dom_scale_hash_u32(hash, DOM_SCALE_DOMAIN_RESOURCES);
    hash = dom_scale_hash_i64(hash, now_tick);
    hash = dom_scale_hash_u32(hash, count);
    for (i = 0u; i < count; ++i) {
        hash = dom_scale_hash_u64(hash, entries[i].resource_id);
        hash = dom_scale_hash_u64(hash, entries[i].quantity);
    }
    return hash;
}

static u64 dom_scale_resource_stat_hash(const dom_scale_resource_entry* entries, u32 count)
{
    u64 b0 = 0u;
    u64 b1 = 0u;
    u64 b2 = 0u;
    u64 b3 = 0u;
    u64 total = 0u;
    u64 hash = dom_scale_fnv1a64_init();
    dom_scale_resource_buckets(entries, count, &b0, &b1, &b2, &b3, &total);
    hash = dom_scale_hash_u32(hash, DOM_SCALE_DOMAIN_RESOURCES);
    hash = dom_scale_hash_u64(hash, b0);
    hash = dom_scale_hash_u64(hash, b1);
    hash = dom_scale_hash_u64(hash, b2);
    hash = dom_scale_hash_u64(hash, b3);
    hash = dom_scale_hash_u64(hash, total);
    return hash;
}

static u64 dom_scale_network_invariant_hash(const dom_scale_network_node* nodes,
                                            u32 node_count,
                                            const dom_scale_network_edge* edges,
                                            u32 edge_count,
                                            dom_act_time_t now_tick)
{
    u64 hash = dom_scale_fnv1a64_init();
    u32 i;
    hash = dom_scale_hash_u32(hash, DOM_SCALE_DOMAIN_NETWORK);
    hash = dom_scale_hash_i64(hash, now_tick);
    hash = dom_scale_hash_u32(hash, node_count);
    for (i = 0u; i < node_count; ++i) {
        hash = dom_scale_hash_u64(hash, nodes[i].node_id);
        hash = dom_scale_hash_u32(hash, nodes[i].node_kind);
    }
    hash = dom_scale_hash_u32(hash, edge_count);
    for (i = 0u; i < edge_count; ++i) {
        hash = dom_scale_hash_u64(hash, edges[i].edge_id);
        hash = dom_scale_hash_u64(hash, edges[i].from_node_id);
        hash = dom_scale_hash_u64(hash, edges[i].to_node_id);
        hash = dom_scale_hash_u64(hash, edges[i].capacity_units);
        hash = dom_scale_hash_u64(hash, edges[i].buffer_units);
    }
    return hash;
}

static u64 dom_scale_network_stat_hash(const dom_scale_network_edge* edges, u32 edge_count)
{
    u32 b0 = 0u;
    u32 b1 = 0u;
    u32 b2 = 0u;
    u32 b3 = 0u;
    u32 mean = 0u;
    u32 p95 = 0u;
    u64 hash = dom_scale_fnv1a64_init();
    dom_scale_wear_distribution(edges, edge_count, &b0, &b1, &b2, &b3, &mean, &p95);
    hash = dom_scale_hash_u32(hash, DOM_SCALE_DOMAIN_NETWORK);
    hash = dom_scale_hash_u32(hash, b0);
    hash = dom_scale_hash_u32(hash, b1);
    hash = dom_scale_hash_u32(hash, b2);
    hash = dom_scale_hash_u32(hash, b3);
    hash = dom_scale_hash_u32(hash, mean);
    hash = dom_scale_hash_u32(hash, p95);
    return hash;
}

static u64 dom_scale_agent_invariant_hash(const dom_scale_agent_entry* agents,
                                          u32 count,
                                          dom_act_time_t now_tick)
{
    u64 hash = dom_scale_fnv1a64_init();
    (void)agents;
    hash = dom_scale_hash_u32(hash, DOM_SCALE_DOMAIN_AGENTS);
    hash = dom_scale_hash_i64(hash, now_tick);
    hash = dom_scale_hash_u32(hash, count);
    return hash;
}

static u64 dom_scale_agent_stat_hash(const dom_scale_agent_entry* agents, u32 count)
{
    dom_scale_role_trait_bucket* role_trait = 0;
    dom_scale_planning_bucket* planning = 0;
    u32 role_trait_count = 0u;
    u32 planning_count = 0u;
    u32 i;
    u64 hash = dom_scale_fnv1a64_init();
    role_trait = (dom_scale_role_trait_bucket*)malloc(sizeof(dom_scale_role_trait_bucket) * (size_t)(count ? count : 1u));
    planning = (dom_scale_planning_bucket*)malloc(sizeof(dom_scale_planning_bucket) * (size_t)(count ? count : 1u));
    if (!role_trait || !planning) {
        free(role_trait);
        free(planning);
        return 0u;
    }
    memset(role_trait, 0, sizeof(dom_scale_role_trait_bucket) * (size_t)(count ? count : 1u));
    memset(planning, 0, sizeof(dom_scale_planning_bucket) * (size_t)(count ? count : 1u));
    for (i = 0u; i < count; ++i) {
        role_trait_count = dom_scale_bucket_insert_role_trait(role_trait,
                                                              role_trait_count,
                                                              count,
                                                              agents[i].role_id,
                                                              agents[i].trait_mask);
        planning_count = dom_scale_bucket_insert_planning(planning,
                                                          planning_count,
                                                          count,
                                                          agents[i].planning_bucket);
    }
    hash = dom_scale_hash_u32(hash, DOM_SCALE_DOMAIN_AGENTS);
    hash = dom_scale_hash_u32(hash, role_trait_count);
    for (i = 0u; i < role_trait_count; ++i) {
        hash = dom_scale_hash_u32(hash, role_trait[i].role_id);
        hash = dom_scale_hash_u32(hash, role_trait[i].trait_mask);
        hash = dom_scale_hash_u32(hash, role_trait[i].count);
    }
    hash = dom_scale_hash_u32(hash, planning_count);
    for (i = 0u; i < planning_count; ++i) {
        hash = dom_scale_hash_u32(hash, planning[i].planning_bucket);
        hash = dom_scale_hash_u32(hash, planning[i].count);
    }
    free(role_trait);
    free(planning);
    return hash;
}

u64 dom_scale_domain_hash(const dom_scale_domain_slot* slot,
                          dom_act_time_t now_tick,
                          u32 worker_count)
{
    u64 inv_hash = 0u;
    u64 stat_hash = 0u;
    (void)worker_count;
    if (!slot) {
        return 0u;
    }
    if (slot->domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        dom_scale_resource_entry* temp = 0;
        u32 count = slot->resources.count;
        temp = (dom_scale_resource_entry*)malloc(sizeof(dom_scale_resource_entry) * (size_t)(count ? count : 1u));
        if (!temp) {
            return 0u;
        }
        if (count > 0u) {
            memcpy(temp, slot->resources.entries, sizeof(dom_scale_resource_entry) * (size_t)count);
            dom_scale_resource_sort(temp, count);
        }
        inv_hash = dom_scale_resource_invariant_hash(temp, count, now_tick);
        stat_hash = dom_scale_resource_stat_hash(temp, count);
        free(temp);
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        dom_scale_network_node* nodes = 0;
        dom_scale_network_edge* edges = 0;
        u32 node_count = slot->network.node_count;
        u32 edge_count = slot->network.edge_count;
        nodes = (dom_scale_network_node*)malloc(sizeof(dom_scale_network_node) * (size_t)(node_count ? node_count : 1u));
        edges = (dom_scale_network_edge*)malloc(sizeof(dom_scale_network_edge) * (size_t)(edge_count ? edge_count : 1u));
        if (!nodes || !edges) {
            free(nodes);
            free(edges);
            return 0u;
        }
        if (node_count > 0u) {
            memcpy(nodes, slot->network.nodes, sizeof(dom_scale_network_node) * (size_t)node_count);
            dom_scale_node_sort(nodes, node_count);
        }
        if (edge_count > 0u) {
            memcpy(edges, slot->network.edges, sizeof(dom_scale_network_edge) * (size_t)edge_count);
            dom_scale_edge_sort(edges, edge_count);
        }
        inv_hash = dom_scale_network_invariant_hash(nodes, node_count, edges, edge_count, now_tick);
        stat_hash = dom_scale_network_stat_hash(edges, edge_count);
        free(nodes);
        free(edges);
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        dom_scale_agent_entry* agents = 0;
        u32 count = slot->agents.count;
        agents = (dom_scale_agent_entry*)malloc(sizeof(dom_scale_agent_entry) * (size_t)(count ? count : 1u));
        if (!agents) {
            return 0u;
        }
        if (count > 0u) {
            memcpy(agents, slot->agents.entries, sizeof(dom_scale_agent_entry) * (size_t)count);
            dom_scale_agent_sort(agents, count);
        }
        inv_hash = dom_scale_agent_invariant_hash(agents, count, now_tick);
        stat_hash = dom_scale_agent_stat_hash(agents, count);
        free(agents);
    } else {
        return 0u;
    }
    {
        u64 hash = dom_scale_fnv1a64_init();
        hash = dom_scale_hash_u64(hash, inv_hash);
        hash = dom_scale_hash_u64(hash, stat_hash);
        return hash;
    }
}

typedef struct dom_scale_writer {
    unsigned char* bytes;
    size_t size;
    size_t used;
    int failed;
} dom_scale_writer;

typedef struct dom_scale_reader {
    const unsigned char* bytes;
    size_t size;
    size_t pos;
    int failed;
} dom_scale_reader;

static void dom_scale_writer_init(dom_scale_writer* w, unsigned char* bytes, size_t size)
{
    if (!w) {
        return;
    }
    w->bytes = bytes;
    w->size = size;
    w->used = 0u;
    w->failed = 0;
}

static void dom_scale_writer_write_bytes(dom_scale_writer* w, const unsigned char* src, size_t len)
{
    if (!w || w->failed || !w->bytes) {
        if (w) {
            w->failed = 1;
        }
        return;
    }
    if (w->used + len > w->size) {
        w->failed = 1;
        return;
    }
    if (len > 0u && src) {
        memcpy(w->bytes + w->used, src, len);
    }
    w->used += len;
}

static void dom_scale_writer_write_u32(dom_scale_writer* w, u32 value)
{
    unsigned char bytes[4];
    bytes[0] = (unsigned char)((value >> 24) & 0xFFu);
    bytes[1] = (unsigned char)((value >> 16) & 0xFFu);
    bytes[2] = (unsigned char)((value >> 8) & 0xFFu);
    bytes[3] = (unsigned char)(value & 0xFFu);
    dom_scale_writer_write_bytes(w, bytes, sizeof(bytes));
}

static void dom_scale_writer_write_u64(dom_scale_writer* w, u64 value)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((value >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((value >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((value >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((value >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((value >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((value >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((value >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(value & 0xFFu);
    dom_scale_writer_write_bytes(w, bytes, sizeof(bytes));
}

static void dom_scale_writer_write_i64(dom_scale_writer* w, dom_act_time_t value)
{
    dom_scale_writer_write_u64(w, (u64)value);
}

static void dom_scale_reader_init(dom_scale_reader* r, const unsigned char* bytes, size_t size)
{
    if (!r) {
        return;
    }
    r->bytes = bytes;
    r->size = size;
    r->pos = 0u;
    r->failed = 0;
}

static int dom_scale_reader_read_bytes(dom_scale_reader* r, unsigned char* dst, size_t len)
{
    if (!r || r->failed || !r->bytes) {
        if (r) {
            r->failed = 1;
        }
        return 0;
    }
    if (r->pos + len > r->size) {
        r->failed = 1;
        return 0;
    }
    if (len > 0u && dst) {
        memcpy(dst, r->bytes + r->pos, len);
    }
    r->pos += len;
    return 1;
}

static int dom_scale_reader_read_u32(dom_scale_reader* r, u32* out_value)
{
    unsigned char bytes[4];
    u32 value;
    if (!out_value) {
        return 0;
    }
    if (!dom_scale_reader_read_bytes(r, bytes, sizeof(bytes))) {
        return 0;
    }
    value = ((u32)bytes[0] << 24) |
            ((u32)bytes[1] << 16) |
            ((u32)bytes[2] << 8) |
            (u32)bytes[3];
    *out_value = value;
    return 1;
}

static int dom_scale_reader_read_u64(dom_scale_reader* r, u64* out_value)
{
    unsigned char bytes[8];
    u64 value;
    if (!out_value) {
        return 0;
    }
    if (!dom_scale_reader_read_bytes(r, bytes, sizeof(bytes))) {
        return 0;
    }
    value = ((u64)bytes[0] << 56) |
            ((u64)bytes[1] << 48) |
            ((u64)bytes[2] << 40) |
            ((u64)bytes[3] << 32) |
            ((u64)bytes[4] << 24) |
            ((u64)bytes[5] << 16) |
            ((u64)bytes[6] << 8) |
            (u64)bytes[7];
    *out_value = value;
    return 1;
}

static int dom_scale_reader_read_i64(dom_scale_reader* r, dom_act_time_t* out_value)
{
    u64 value = 0u;
    if (!dom_scale_reader_read_u64(r, &value)) {
        return 0;
    }
    if (out_value) {
        *out_value = (dom_act_time_t)value;
    }
    return 1;
}

typedef struct dom_scale_extension_pair {
    char* key;
    char* value;
} dom_scale_extension_pair;

typedef struct dom_scale_capsule_data {
    dom_scale_capsule_summary summary;
    u64 invariant_hash;
    u64 statistic_hash;
    u32 invariant_count;
    u32 statistic_count;
    u32 schema_len;
    char schema[64];
    unsigned char* extension_bytes;
    u32 extension_len;
    dom_scale_extension_pair* extensions;
    u32 extension_count;
    u32 extension_capacity;
    int extension_parse_ok;
    u32 rng_state_agents_reconstruct;
    int rng_state_agents_present;

    dom_scale_resource_entry* resources;
    u32 resource_count;
    u64 resource_bucket0;
    u64 resource_bucket1;
    u64 resource_bucket2;
    u64 resource_bucket3;
    u64 resource_total_qty;

    dom_scale_network_node* nodes;
    u32 node_count;
    dom_scale_network_edge* edges;
    u32 edge_count;
    u32 wear_bucket0;
    u32 wear_bucket1;
    u32 wear_bucket2;
    u32 wear_bucket3;
    u32 wear_mean;
    u32 wear_p95;

    dom_scale_agent_entry* agents;
    u32 agent_count;
} dom_scale_capsule_data;

static void dom_scale_capsule_data_init(dom_scale_capsule_data* data)
{
    if (!data) {
        return;
    }
    memset(data, 0, sizeof(*data));
}

static void dom_scale_capsule_data_free(dom_scale_capsule_data* data)
{
    if (!data) {
        return;
    }
    free(data->resources);
    free(data->nodes);
    free(data->edges);
    free(data->agents);
    free(data->extension_bytes);
    if (data->extensions) {
        u32 i;
        for (i = 0u; i < data->extension_count; ++i) {
            free(data->extensions[i].key);
            free(data->extensions[i].value);
        }
        free(data->extensions);
    }
    memset(data, 0, sizeof(*data));
}

static char* dom_scale_strdup(const char* text)
{
    size_t len;
    char* copy;
    if (!text) {
        return 0;
    }
    len = strlen(text);
    copy = (char*)malloc(len + 1u);
    if (!copy) {
        return 0;
    }
    memcpy(copy, text, len);
    copy[len] = '\0';
    return copy;
}

static int dom_scale_extension_key_cmp(const char* a, const char* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    return strcmp(a, b);
}

static int dom_scale_extensions_reserve(dom_scale_capsule_data* data, u32 needed)
{
    dom_scale_extension_pair* new_pairs;
    u32 new_capacity;
    u32 i;
    if (!data) {
        return 0;
    }
    if (needed <= data->extension_capacity) {
        return 1;
    }
    new_capacity = data->extension_capacity ? data->extension_capacity : 4u;
    while (new_capacity < needed) {
        if (new_capacity > 0x7FFFFFFFu) {
            new_capacity = needed;
            break;
        }
        new_capacity *= 2u;
    }
    new_pairs = (dom_scale_extension_pair*)realloc(data->extensions,
                                                    sizeof(dom_scale_extension_pair) * (size_t)new_capacity);
    if (!new_pairs) {
        return 0;
    }
    for (i = data->extension_capacity; i < new_capacity; ++i) {
        new_pairs[i].key = 0;
        new_pairs[i].value = 0;
    }
    data->extensions = new_pairs;
    data->extension_capacity = new_capacity;
    return 1;
}

static int dom_scale_extensions_add_or_update(dom_scale_capsule_data* data,
                                              const char* key,
                                              const char* value)
{
    u32 i;
    u32 insert_at = 0u;
    char* key_copy;
    char* value_copy;
    if (!data || !key || !value) {
        return 0;
    }
    for (i = 0u; i < data->extension_count; ++i) {
        dom_scale_extension_pair* pair = &data->extensions[i];
        int cmp = dom_scale_extension_key_cmp(pair->key, key);
        if (cmp == 0) {
            value_copy = dom_scale_strdup(value);
            if (!value_copy) {
                return 0;
            }
            free(pair->value);
            pair->value = value_copy;
            return 1;
        }
        if (cmp > 0) {
            insert_at = i;
            break;
        }
        insert_at = i + 1u;
    }
    if (!dom_scale_extensions_reserve(data, data->extension_count + 1u)) {
        return 0;
    }
    for (i = data->extension_count; i > insert_at; --i) {
        data->extensions[i] = data->extensions[i - 1u];
    }
    key_copy = dom_scale_strdup(key);
    value_copy = dom_scale_strdup(value);
    if (!key_copy || !value_copy) {
        free(key_copy);
        free(value_copy);
        return 0;
    }
    data->extensions[insert_at].key = key_copy;
    data->extensions[insert_at].value = value_copy;
    data->extension_count += 1u;
    return 1;
}

static int dom_scale_extensions_add_or_update_u64(dom_scale_capsule_data* data,
                                                  const char* key,
                                                  u64 value)
{
    char buffer[32];
    (void)snprintf(buffer, sizeof(buffer), "%llu", (unsigned long long)value);
    return dom_scale_extensions_add_or_update(data, key, buffer);
}

static int dom_scale_extensions_add_or_update_i64(dom_scale_capsule_data* data,
                                                  const char* key,
                                                  dom_act_time_t value)
{
    char buffer[32];
    (void)snprintf(buffer, sizeof(buffer), "%lld", (long long)value);
    return dom_scale_extensions_add_or_update(data, key, buffer);
}

static const char* dom_scale_extensions_get(const dom_scale_capsule_data* data,
                                            const char* key)
{
    u32 i;
    if (!data || !data->extensions || !key) {
        return 0;
    }
    for (i = 0u; i < data->extension_count; ++i) {
        const dom_scale_extension_pair* pair = &data->extensions[i];
        if (dom_scale_extension_key_cmp(pair->key, key) == 0) {
            return pair->value;
        }
    }
    return 0;
}

static int dom_scale_extensions_get_u64(const dom_scale_capsule_data* data,
                                        const char* key,
                                        u64* out_value)
{
    const char* text = dom_scale_extensions_get(data, key);
    if (!text || !out_value) {
        return 0;
    }
    return dom_scale_parse_u64_strict(text, out_value);
}

static void dom_scale_extensions_clear(dom_scale_capsule_data* data)
{
    u32 i;
    if (!data) {
        return;
    }
    if (!data->extensions) {
        data->extension_count = 0u;
        data->extension_parse_ok = 0;
        return;
    }
    for (i = 0u; i < data->extension_count; ++i) {
        free(data->extensions[i].key);
        free(data->extensions[i].value);
        data->extensions[i].key = 0;
        data->extensions[i].value = 0;
    }
    data->extension_count = 0u;
    data->extension_parse_ok = 0;
}

static int dom_scale_extensions_parse(dom_scale_capsule_data* data,
                                      const unsigned char* bytes,
                                      u32 len)
{
    dom_scale_reader reader;
    u32 ext_count = 0u;
    u32 i;
    if (!data) {
        return 0;
    }
    data->extension_parse_ok = 0;
    free(data->extension_bytes);
    data->extension_bytes = 0;
    data->extension_len = len;
    if (len > 0u && bytes) {
        data->extension_bytes = (unsigned char*)malloc((size_t)len);
        if (!data->extension_bytes) {
            return 0;
        }
        memcpy(data->extension_bytes, bytes, (size_t)len);
    }
    dom_scale_extensions_clear(data);
    if (!bytes || len == 0u) {
        data->extension_parse_ok = 1;
        return 1;
    }
    dom_scale_reader_init(&reader, bytes, (size_t)len);
    if (!dom_scale_reader_read_u32(&reader, &ext_count)) {
        return 1;
    }
    for (i = 0u; i < ext_count; ++i) {
        u32 key_len = 0u;
        u32 value_len = 0u;
        char* key = 0;
        char* value = 0;
        if (!dom_scale_reader_read_u32(&reader, &key_len) ||
            key_len == 0u ||
            key_len > (u32)(len - (u32)reader.pos)) {
            return 1;
        }
        key = (char*)malloc((size_t)key_len + 1u);
        if (!key) {
            return 1;
        }
        if (!dom_scale_reader_read_bytes(&reader, (unsigned char*)key, (size_t)key_len)) {
            free(key);
            return 1;
        }
        key[key_len] = '\0';
        if (!dom_scale_reader_read_u32(&reader, &value_len) ||
            value_len > (u32)(len - (u32)reader.pos)) {
            free(key);
            return 1;
        }
        value = (char*)malloc((size_t)value_len + 1u);
        if (!value) {
            free(key);
            return 1;
        }
        if (!dom_scale_reader_read_bytes(&reader, (unsigned char*)value, (size_t)value_len)) {
            free(key);
            free(value);
            return 1;
        }
        value[value_len] = '\0';
        (void)dom_scale_extensions_add_or_update(data, key, value);
        free(key);
        free(value);
    }
    if (!reader.failed && reader.pos == reader.size) {
        data->extension_parse_ok = 1;
    }
    return 1;
}

static int dom_scale_extensions_ensure_scale1(dom_scale_capsule_data* data)
{
    if (!data) {
        return 0;
    }
    return dom_scale_extensions_add_or_update(data, "dominium.scale1", "v1");
}

static int dom_scale_extensions_ensure_rng_state(dom_scale_capsule_data* data)
{
    u32 rng_state;
    if (!data) {
        return 0;
    }
    if (data->summary.domain_kind != DOM_SCALE_DOMAIN_AGENTS) {
        return 1;
    }
    rng_state = dom_scale_rng_state_from_seed(data->summary.seed_base,
                                              data->summary.domain_id,
                                              g_scale_rng_stream_agents_reconstruct);
    data->rng_state_agents_reconstruct = rng_state;
    data->rng_state_agents_present = 1;
    return dom_scale_extensions_add_or_update_u64(data,
                                                  g_scale_rng_state_ext_agents_reconstruct,
                                                  rng_state);
}

static size_t dom_scale_extensions_serialized_len(const dom_scale_capsule_data* data)
{
    size_t len = 4u;
    u32 i;
    if (!data) {
        return 0u;
    }
    for (i = 0u; i < data->extension_count; ++i) {
        const dom_scale_extension_pair* pair = &data->extensions[i];
        size_t key_len = pair->key ? strlen(pair->key) : 0u;
        size_t value_len = pair->value ? strlen(pair->value) : 0u;
        len += 4u + key_len;
        len += 4u + value_len;
    }
    return len;
}

static void dom_scale_writer_write_string(dom_scale_writer* w, const char* text);

static void dom_scale_extensions_write(dom_scale_writer* w,
                                       const dom_scale_capsule_data* data)
{
    u32 i;
    u32 count = data ? data->extension_count : 0u;
    dom_scale_writer_write_u32(w, count);
    for (i = 0u; i < count; ++i) {
        const dom_scale_extension_pair* pair = &data->extensions[i];
        dom_scale_writer_write_string(w, pair->key ? pair->key : "");
        dom_scale_writer_write_string(w, pair->value ? pair->value : "");
    }
}

static size_t dom_scale_extension_len(const char* rng_state_value)
{
    const char* key = "dominium.scale1";
    const char* value = "v1";
    const char* rng_key = g_scale_rng_state_ext_agents_reconstruct;
    int has_rng = (rng_state_value && *rng_state_value) ? 1 : 0;
    size_t len = 0u;
    len += 4u; /* ext_count */
    len += 4u + strlen(key);
    len += 4u + strlen(value);
    if (has_rng) {
        len += 4u + strlen(rng_key);
        len += 4u + strlen(rng_state_value);
    }
    return len;
}

static void dom_scale_write_extensions(dom_scale_writer* w, const char* rng_state_value)
{
    const char* key = "dominium.scale1";
    const char* value = "v1";
    const char* rng_key = g_scale_rng_state_ext_agents_reconstruct;
    int has_rng = (rng_state_value && *rng_state_value) ? 1 : 0;
    dom_scale_writer_write_u32(w, has_rng ? 2u : 1u);
    dom_scale_writer_write_u32(w, (u32)strlen(key));
    dom_scale_writer_write_bytes(w, (const unsigned char*)key, strlen(key));
    dom_scale_writer_write_u32(w, (u32)strlen(value));
    dom_scale_writer_write_bytes(w, (const unsigned char*)value, strlen(value));
    if (has_rng) {
        dom_scale_writer_write_u32(w, (u32)strlen(rng_key));
        dom_scale_writer_write_bytes(w, (const unsigned char*)rng_key, strlen(rng_key));
        dom_scale_writer_write_u32(w, (u32)strlen(rng_state_value));
        dom_scale_writer_write_bytes(w, (const unsigned char*)rng_state_value, strlen(rng_state_value));
    }
}

static const char* g_scale_invariant_ids[] = {
    "SCALE0-PROJECTION-001",
    "SCALE0-CONSERVE-002",
    "SCALE0-COMMIT-003",
    "SCALE0-DETERMINISM-004",
    "SCALE0-NO-EXNIHILO-007",
    "SCALE0-REPLAY-008"
};

static const char* g_scale_stat_ids_resources[] = {
    "DOM-SCALE-RESOURCE-BUCKETS"
};

static const char* g_scale_stat_ids_network[] = {
    "STAT-SCALE-WEAR-DIST"
};

static const char* g_scale_stat_ids_agents[] = {
    "DOM-SCALE-ROLE-TRAIT-DIST",
    "DOM-SCALE-PLANNING-HORIZON-DIST"
};

static size_t dom_scale_string_list_len(const char* const* items, u32 count)
{
    size_t len = 4u;
    u32 i;
    for (i = 0u; i < count; ++i) {
        len += 4u;
        len += strlen(items[i]);
    }
    return len;
}

static void dom_scale_writer_write_string(dom_scale_writer* w, const char* text)
{
    size_t len = text ? strlen(text) : 0u;
    dom_scale_writer_write_u32(w, (u32)len);
    dom_scale_writer_write_bytes(w, (const unsigned char*)text, len);
}

static void dom_scale_writer_write_string_list(dom_scale_writer* w,
                                               const char* const* items,
                                               u32 count)
{
    u32 i;
    dom_scale_writer_write_u32(w, count);
    for (i = 0u; i < count; ++i) {
        dom_scale_writer_write_string(w, items[i]);
    }
}

static int dom_scale_reader_skip(dom_scale_reader* r, size_t len)
{
    return dom_scale_reader_read_bytes(r, 0, len);
}

static int dom_scale_reader_skip_string(dom_scale_reader* r)
{
    u32 len = 0u;
    if (!dom_scale_reader_read_u32(r, &len)) {
        return 0;
    }
    return dom_scale_reader_skip(r, (size_t)len);
}

static int dom_scale_reader_skip_string_list(dom_scale_reader* r, u32* out_count)
{
    u32 count = 0u;
    u32 i;
    if (!dom_scale_reader_read_u32(r, &count)) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (!dom_scale_reader_skip_string(r)) {
            return 0;
        }
    }
    if (out_count) {
        *out_count = count;
    }
    return 1;
}

static int dom_scale_reader_read_string(dom_scale_reader* r,
                                        char* buffer,
                                        size_t capacity,
                                        u32* out_len)
{
    u32 len = 0u;
    if (!buffer || capacity == 0u) {
        return 0;
    }
    if (!dom_scale_reader_read_u32(r, &len)) {
        return 0;
    }
    if ((size_t)len >= capacity) {
        return 0;
    }
    if (!dom_scale_reader_read_bytes(r, (unsigned char*)buffer, (size_t)len)) {
        return 0;
    }
    buffer[len] = '\0';
    if (out_len) {
        *out_len = len;
    }
    return 1;
}

static int dom_scale_agent_buckets(const dom_scale_agent_entry* agents,
                                   u32 count,
                                   dom_scale_role_trait_bucket** out_role_trait,
                                   u32* out_role_trait_count,
                                   dom_scale_planning_bucket** out_planning,
                                   u32* out_planning_count)
{
    dom_scale_role_trait_bucket* role_trait = 0;
    dom_scale_planning_bucket* planning = 0;
    u32 role_trait_count = 0u;
    u32 planning_count = 0u;
    u32 i;
    role_trait = (dom_scale_role_trait_bucket*)malloc(sizeof(dom_scale_role_trait_bucket) * (size_t)(count ? count : 1u));
    planning = (dom_scale_planning_bucket*)malloc(sizeof(dom_scale_planning_bucket) * (size_t)(count ? count : 1u));
    if (!role_trait || !planning) {
        free(role_trait);
        free(planning);
        return 0;
    }
    memset(role_trait, 0, sizeof(dom_scale_role_trait_bucket) * (size_t)(count ? count : 1u));
    memset(planning, 0, sizeof(dom_scale_planning_bucket) * (size_t)(count ? count : 1u));
    for (i = 0u; i < count; ++i) {
        role_trait_count = dom_scale_bucket_insert_role_trait(role_trait,
                                                              role_trait_count,
                                                              count,
                                                              agents[i].role_id,
                                                              agents[i].trait_mask);
        planning_count = dom_scale_bucket_insert_planning(planning,
                                                          planning_count,
                                                          count,
                                                          agents[i].planning_bucket);
    }
    if (out_role_trait) {
        *out_role_trait = role_trait;
    } else {
        free(role_trait);
        role_trait = 0;
    }
    if (out_planning) {
        *out_planning = planning;
    } else {
        free(planning);
        planning = 0;
    }
    if (out_role_trait_count) {
        *out_role_trait_count = role_trait_count;
    }
    if (out_planning_count) {
        *out_planning_count = planning_count;
    }
    return 1;
}

static size_t dom_scale_payload_size_resources(u32 resource_count)
{
    size_t size = 0u;
    size += 4u; /* count */
    size += (size_t)resource_count * 16u;
    size += 40u; /* buckets */
    return size;
}

static size_t dom_scale_payload_size_network(u32 node_count, u32 edge_count)
{
    size_t size = 0u;
    size += 4u; /* node count */
    size += (size_t)node_count * 12u;
    size += 4u; /* edge count */
    size += (size_t)edge_count * 56u;
    size += 24u; /* wear stats */
    return size;
}

static size_t dom_scale_payload_size_agents(u32 agent_count,
                                            u32 role_trait_count,
                                            u32 planning_count)
{
    size_t size = 0u;
    size += 4u; /* agent count */
    size += (size_t)agent_count * 20u;
    size += 4u; /* role trait count */
    size += (size_t)role_trait_count * 12u;
    size += 4u; /* planning count */
    size += (size_t)planning_count * 8u;
    return size;
}

static size_t dom_scale_header_size(size_t schema_len,
                                    size_t invariant_list_len,
                                    size_t stat_list_len)
{
    size_t size = 0u;
    size += 4u; /* version */
    size += 4u + schema_len;
    size += 8u; /* capsule id */
    size += 8u; /* domain id */
    size += 4u; /* domain kind */
    size += 8u; /* source tick */
    size += 4u; /* reason */
    size += 4u; /* seed */
    size += 8u; /* invariant hash */
    size += 8u; /* stat hash */
    size += invariant_list_len;
    size += stat_list_len;
    size += 4u; /* extension len */
    return size;
}

static void dom_scale_write_resources_payload(dom_scale_writer* w,
                                              const dom_scale_resource_entry* entries,
                                              u32 count)
{
    u32 i;
    u64 b0 = 0u;
    u64 b1 = 0u;
    u64 b2 = 0u;
    u64 b3 = 0u;
    u64 total = 0u;
    dom_scale_resource_buckets(entries, count, &b0, &b1, &b2, &b3, &total);
    dom_scale_writer_write_u32(w, count);
    for (i = 0u; i < count; ++i) {
        dom_scale_writer_write_u64(w, entries[i].resource_id);
        dom_scale_writer_write_u64(w, entries[i].quantity);
    }
    dom_scale_writer_write_u64(w, b0);
    dom_scale_writer_write_u64(w, b1);
    dom_scale_writer_write_u64(w, b2);
    dom_scale_writer_write_u64(w, b3);
    dom_scale_writer_write_u64(w, total);
}

static void dom_scale_write_network_payload(dom_scale_writer* w,
                                            const dom_scale_network_node* nodes,
                                            u32 node_count,
                                            const dom_scale_network_edge* edges,
                                            u32 edge_count)
{
    u32 i;
    u32 b0 = 0u;
    u32 b1 = 0u;
    u32 b2 = 0u;
    u32 b3 = 0u;
    u32 mean = 0u;
    u32 p95 = 0u;
    dom_scale_wear_distribution(edges, edge_count, &b0, &b1, &b2, &b3, &mean, &p95);
    dom_scale_writer_write_u32(w, node_count);
    for (i = 0u; i < node_count; ++i) {
        dom_scale_writer_write_u64(w, nodes[i].node_id);
        dom_scale_writer_write_u32(w, nodes[i].node_kind);
    }
    dom_scale_writer_write_u32(w, edge_count);
    for (i = 0u; i < edge_count; ++i) {
        dom_scale_writer_write_u64(w, edges[i].edge_id);
        dom_scale_writer_write_u64(w, edges[i].from_node_id);
        dom_scale_writer_write_u64(w, edges[i].to_node_id);
        dom_scale_writer_write_u64(w, edges[i].capacity_units);
        dom_scale_writer_write_u64(w, edges[i].buffer_units);
        dom_scale_writer_write_u32(w, edges[i].wear_bucket0);
        dom_scale_writer_write_u32(w, edges[i].wear_bucket1);
        dom_scale_writer_write_u32(w, edges[i].wear_bucket2);
        dom_scale_writer_write_u32(w, edges[i].wear_bucket3);
    }
    dom_scale_writer_write_u32(w, b0);
    dom_scale_writer_write_u32(w, b1);
    dom_scale_writer_write_u32(w, b2);
    dom_scale_writer_write_u32(w, b3);
    dom_scale_writer_write_u32(w, mean);
    dom_scale_writer_write_u32(w, p95);
}

static void dom_scale_write_agents_payload(dom_scale_writer* w,
                                           const dom_scale_agent_entry* agents,
                                           u32 agent_count,
                                           const dom_scale_role_trait_bucket* role_trait,
                                           u32 role_trait_count,
                                           const dom_scale_planning_bucket* planning,
                                           u32 planning_count)
{
    u32 i;
    dom_scale_writer_write_u32(w, agent_count);
    for (i = 0u; i < agent_count; ++i) {
        dom_scale_writer_write_u64(w, agents[i].agent_id);
        dom_scale_writer_write_u32(w, agents[i].role_id);
        dom_scale_writer_write_u32(w, agents[i].trait_mask);
        dom_scale_writer_write_u32(w, agents[i].planning_bucket);
    }
    dom_scale_writer_write_u32(w, role_trait_count);
    for (i = 0u; i < role_trait_count; ++i) {
        dom_scale_writer_write_u32(w, role_trait[i].role_id);
        dom_scale_writer_write_u32(w, role_trait[i].trait_mask);
        dom_scale_writer_write_u32(w, role_trait[i].count);
    }
    dom_scale_writer_write_u32(w, planning_count);
    for (i = 0u; i < planning_count; ++i) {
        dom_scale_writer_write_u32(w, planning[i].planning_bucket);
        dom_scale_writer_write_u32(w, planning[i].count);
    }
}

typedef struct dom_scale_serialized_domain {
    u32 domain_kind;
    size_t payload_len;
    u64 invariant_hash;
    u64 statistic_hash;

    dom_scale_resource_entry* resources;
    u32 resource_count;

    dom_scale_network_node* nodes;
    u32 node_count;
    dom_scale_network_edge* edges;
    u32 edge_count;

    dom_scale_agent_entry* agents;
    u32 agent_count;
    dom_scale_role_trait_bucket* role_trait;
    u32 role_trait_count;
    dom_scale_planning_bucket* planning;
    u32 planning_count;
} dom_scale_serialized_domain;

static void dom_scale_serialized_domain_free(dom_scale_serialized_domain* dom)
{
    if (!dom) {
        return;
    }
    free(dom->resources);
    free(dom->nodes);
    free(dom->edges);
    free(dom->agents);
    free(dom->role_trait);
    free(dom->planning);
    memset(dom, 0, sizeof(*dom));
}

static int dom_scale_build_serialized_domain(const dom_scale_domain_slot* slot,
                                             dom_act_time_t now_tick,
                                             dom_scale_serialized_domain* out_dom)
{
    if (!slot || !out_dom) {
        return 0;
    }
    memset(out_dom, 0, sizeof(*out_dom));
    out_dom->domain_kind = slot->domain_kind;
    if (slot->domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        u32 count = slot->resources.count;
        dom_scale_resource_entry* copy = 0;
        if (count > 0u && !slot->resources.entries) {
            return 0;
        }
        copy = (dom_scale_resource_entry*)malloc(sizeof(dom_scale_resource_entry) * (size_t)(count ? count : 1u));
        if (!copy) {
            return 0;
        }
        if (count > 0u) {
            memcpy(copy, slot->resources.entries, sizeof(dom_scale_resource_entry) * (size_t)count);
            dom_scale_resource_sort(copy, count);
        }
        out_dom->resources = copy;
        out_dom->resource_count = count;
        out_dom->payload_len = dom_scale_payload_size_resources(count);
        out_dom->invariant_hash = dom_scale_resource_invariant_hash(copy, count, now_tick);
        out_dom->statistic_hash = dom_scale_resource_stat_hash(copy, count);
        return 1;
    }
    if (slot->domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        u32 node_count = slot->network.node_count;
        u32 edge_count = slot->network.edge_count;
        dom_scale_network_node* nodes = 0;
        dom_scale_network_edge* edges = 0;
        if ((node_count > 0u && !slot->network.nodes) ||
            (edge_count > 0u && !slot->network.edges)) {
            return 0;
        }
        nodes = (dom_scale_network_node*)malloc(sizeof(dom_scale_network_node) * (size_t)(node_count ? node_count : 1u));
        edges = (dom_scale_network_edge*)malloc(sizeof(dom_scale_network_edge) * (size_t)(edge_count ? edge_count : 1u));
        if (!nodes || !edges) {
            free(nodes);
            free(edges);
            return 0;
        }
        if (node_count > 0u) {
            memcpy(nodes, slot->network.nodes, sizeof(dom_scale_network_node) * (size_t)node_count);
            dom_scale_node_sort(nodes, node_count);
        }
        if (edge_count > 0u) {
            memcpy(edges, slot->network.edges, sizeof(dom_scale_network_edge) * (size_t)edge_count);
            dom_scale_edge_sort(edges, edge_count);
        }
        out_dom->nodes = nodes;
        out_dom->node_count = node_count;
        out_dom->edges = edges;
        out_dom->edge_count = edge_count;
        out_dom->payload_len = dom_scale_payload_size_network(node_count, edge_count);
        out_dom->invariant_hash = dom_scale_network_invariant_hash(nodes, node_count, edges, edge_count, now_tick);
        out_dom->statistic_hash = dom_scale_network_stat_hash(edges, edge_count);
        return 1;
    }
    if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        u32 count = slot->agents.count;
        dom_scale_agent_entry* agents = 0;
        dom_scale_role_trait_bucket* role_trait = 0;
        dom_scale_planning_bucket* planning = 0;
        u32 role_trait_count = 0u;
        u32 planning_count = 0u;
        if (count > 0u && !slot->agents.entries) {
            return 0;
        }
        agents = (dom_scale_agent_entry*)malloc(sizeof(dom_scale_agent_entry) * (size_t)(count ? count : 1u));
        if (!agents) {
            return 0;
        }
        if (count > 0u) {
            memcpy(agents, slot->agents.entries, sizeof(dom_scale_agent_entry) * (size_t)count);
            dom_scale_agent_sort(agents, count);
        }
        if (!dom_scale_agent_buckets(agents,
                                     count,
                                     &role_trait,
                                     &role_trait_count,
                                     &planning,
                                     &planning_count)) {
            free(agents);
            return 0;
        }
        out_dom->agents = agents;
        out_dom->agent_count = count;
        out_dom->role_trait = role_trait;
        out_dom->role_trait_count = role_trait_count;
        out_dom->planning = planning;
        out_dom->planning_count = planning_count;
        out_dom->payload_len = dom_scale_payload_size_agents(count, role_trait_count, planning_count);
        out_dom->invariant_hash = dom_scale_agent_invariant_hash(agents, count, now_tick);
        out_dom->statistic_hash = dom_scale_agent_stat_hash(agents, count);
        return 1;
    }
    return 1;
}

static int dom_scale_serialize_capsule(const dom_scale_domain_slot* slot,
                                       dom_act_time_t now_tick,
                                       u32 reason_code,
                                       u64 capsule_id,
                                       u32 seed_base,
                                       unsigned char** out_bytes,
                                       u32* out_byte_count,
                                       u64* out_invariant_hash,
                                       u64* out_statistic_hash,
                                       u32* out_invariant_count,
                                       u32* out_statistic_count)
{
    const char* const* stat_ids = 0;
    u32 stat_id_count = 0u;
    u32 invariant_id_count = (u32)(sizeof(g_scale_invariant_ids) / sizeof(g_scale_invariant_ids[0]));
    size_t schema_len = strlen(DOM_SCALE_MACRO_CAPSULE_SCHEMA);
    size_t invariant_list_len = dom_scale_string_list_len(g_scale_invariant_ids, invariant_id_count);
    size_t stat_list_len = 0u;
    size_t extension_len = 0u;
    size_t payload_len = 0u;
    size_t total_len = 0u;
    unsigned char* bytes = 0;
    dom_scale_writer writer;
    u64 invariant_hash = 0u;
    u64 statistic_hash = 0u;
    char rng_state_value[32];
    const char* rng_value_ptr = 0;

    if (!slot || !out_bytes || !out_byte_count) {
        return -1;
    }

    if (slot->domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        stat_ids = g_scale_stat_ids_resources;
        stat_id_count = (u32)(sizeof(g_scale_stat_ids_resources) / sizeof(g_scale_stat_ids_resources[0]));
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        stat_ids = g_scale_stat_ids_network;
        stat_id_count = (u32)(sizeof(g_scale_stat_ids_network) / sizeof(g_scale_stat_ids_network[0]));
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        stat_ids = g_scale_stat_ids_agents;
        stat_id_count = (u32)(sizeof(g_scale_stat_ids_agents) / sizeof(g_scale_stat_ids_agents[0]));
    } else {
        return -2;
    }
    stat_list_len = dom_scale_string_list_len(stat_ids, stat_id_count);

    {
        dom_scale_serialized_domain dom;
        if (!dom_scale_build_serialized_domain(slot, now_tick, &dom)) {
            return -3;
        }
        payload_len = dom.payload_len;
        invariant_hash = dom.invariant_hash;
        statistic_hash = dom.statistic_hash;
        if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
            u32 rng_state = dom_scale_rng_state_from_seed(seed_base,
                                                          slot->domain_id,
                                                          g_scale_rng_stream_agents_reconstruct);
            (void)snprintf(rng_state_value, sizeof(rng_state_value), "%u", rng_state);
            rng_value_ptr = rng_state_value;
        }
        extension_len = dom_scale_extension_len(rng_value_ptr);
        total_len = dom_scale_header_size(schema_len, invariant_list_len, stat_list_len) +
                    payload_len + extension_len;
        bytes = (unsigned char*)malloc(total_len);
        if (!bytes) {
            dom_scale_serialized_domain_free(&dom);
            return -4;
        }
        dom_scale_writer_init(&writer, bytes, total_len);
        dom_scale_writer_write_u32(&writer, DOM_SCALE_MACRO_CAPSULE_VERSION);
        dom_scale_writer_write_string(&writer, DOM_SCALE_MACRO_CAPSULE_SCHEMA);
        dom_scale_writer_write_u64(&writer, capsule_id);
        dom_scale_writer_write_u64(&writer, slot->domain_id);
        dom_scale_writer_write_u32(&writer, slot->domain_kind);
        dom_scale_writer_write_i64(&writer, now_tick);
        dom_scale_writer_write_u32(&writer, reason_code);
        dom_scale_writer_write_u32(&writer, seed_base);
        dom_scale_writer_write_u64(&writer, invariant_hash);
        dom_scale_writer_write_u64(&writer, statistic_hash);
        dom_scale_writer_write_string_list(&writer, g_scale_invariant_ids, invariant_id_count);
        dom_scale_writer_write_string_list(&writer, stat_ids, stat_id_count);
        dom_scale_writer_write_u32(&writer, (u32)extension_len);
        if (dom.domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
            dom_scale_write_resources_payload(&writer, dom.resources, dom.resource_count);
        } else if (dom.domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
            dom_scale_write_network_payload(&writer, dom.nodes, dom.node_count, dom.edges, dom.edge_count);
        } else if (dom.domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
            dom_scale_write_agents_payload(&writer,
                                           dom.agents,
                                           dom.agent_count,
                                           dom.role_trait,
                                           dom.role_trait_count,
                                           dom.planning,
                                           dom.planning_count);
        }
        dom_scale_write_extensions(&writer, rng_value_ptr);
        if (!writer.failed && writer.used != total_len) {
            writer.failed = 1;
        }
        if (writer.failed) {
            dom_scale_serialized_domain_free(&dom);
            free(bytes);
            return -5;
        }
        *out_bytes = bytes;
        *out_byte_count = (u32)writer.used;
        if (out_invariant_hash) {
            *out_invariant_hash = invariant_hash;
        }
        if (out_statistic_hash) {
            *out_statistic_hash = statistic_hash;
        }
        if (out_invariant_count) {
            *out_invariant_count = invariant_id_count;
        }
        if (out_statistic_count) {
            *out_statistic_count = stat_id_count;
        }
        dom_scale_serialized_domain_free(&dom);
        return 0;
    }
}

static void dom_scale_slot_from_data(const dom_scale_capsule_data* data,
                                     dom_scale_domain_slot* slot)
{
    if (!data || !slot) {
        return;
    }
    memset(slot, 0, sizeof(*slot));
    slot->domain_id = data->summary.domain_id;
    slot->domain_kind = data->summary.domain_kind;
    if (slot->domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        slot->resources.entries = data->resources;
        slot->resources.count = data->resource_count;
        slot->resources.capacity = data->resource_count;
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        slot->network.nodes = data->nodes;
        slot->network.node_count = data->node_count;
        slot->network.node_capacity = data->node_count;
        slot->network.edges = data->edges;
        slot->network.edge_count = data->edge_count;
        slot->network.edge_capacity = data->edge_count;
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        slot->agents.entries = data->agents;
        slot->agents.count = data->agent_count;
        slot->agents.capacity = data->agent_count;
    }
}

static int dom_scale_stat_ids_for_kind(u32 domain_kind,
                                       const char* const** out_ids,
                                       u32* out_count)
{
    if (!out_ids || !out_count) {
        return 0;
    }
    *out_ids = 0;
    *out_count = 0u;
    if (domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        *out_ids = g_scale_stat_ids_resources;
        *out_count = (u32)(sizeof(g_scale_stat_ids_resources) / sizeof(g_scale_stat_ids_resources[0]));
        return 1;
    }
    if (domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        *out_ids = g_scale_stat_ids_network;
        *out_count = (u32)(sizeof(g_scale_stat_ids_network) / sizeof(g_scale_stat_ids_network[0]));
        return 1;
    }
    if (domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        *out_ids = g_scale_stat_ids_agents;
        *out_count = (u32)(sizeof(g_scale_stat_ids_agents) / sizeof(g_scale_stat_ids_agents[0]));
        return 1;
    }
    return 0;
}

static int dom_scale_serialize_capsule_from_data(dom_scale_capsule_data* data,
                                                 unsigned char** out_bytes,
                                                 u32* out_byte_count,
                                                 u64* out_invariant_hash,
                                                 u64* out_statistic_hash,
                                                 u32* out_invariant_count,
                                                 u32* out_statistic_count)
{
    const char* const* stat_ids = 0;
    u32 stat_id_count = 0u;
    u32 invariant_id_count = (u32)(sizeof(g_scale_invariant_ids) / sizeof(g_scale_invariant_ids[0]));
    size_t schema_len = strlen(DOM_SCALE_MACRO_CAPSULE_SCHEMA);
    size_t invariant_list_len = dom_scale_string_list_len(g_scale_invariant_ids, invariant_id_count);
    size_t stat_list_len = 0u;
    size_t extension_len = 0u;
    size_t payload_len = 0u;
    size_t total_len = 0u;
    unsigned char* bytes = 0;
    dom_scale_writer writer;
    dom_scale_domain_slot slot;
    dom_scale_serialized_domain dom;
    u64 invariant_hash = 0u;
    u64 statistic_hash = 0u;

    if (!data || !out_bytes || !out_byte_count) {
        return -1;
    }
    if (!dom_scale_stat_ids_for_kind(data->summary.domain_kind, &stat_ids, &stat_id_count)) {
        return -2;
    }
    stat_list_len = dom_scale_string_list_len(stat_ids, stat_id_count);

    if (!dom_scale_extensions_ensure_scale1(data)) {
        return -3;
    }
    if (!dom_scale_extensions_ensure_rng_state(data)) {
        return -3;
    }

    dom_scale_slot_from_data(data, &slot);
    memset(&dom, 0, sizeof(dom));
    if (!dom_scale_build_serialized_domain(&slot, data->summary.source_tick, &dom)) {
        return -4;
    }
    payload_len = dom.payload_len;
    invariant_hash = dom.invariant_hash;
    statistic_hash = dom.statistic_hash;
    extension_len = dom_scale_extensions_serialized_len(data);
    total_len = dom_scale_header_size(schema_len, invariant_list_len, stat_list_len) +
                payload_len + extension_len;
    bytes = (unsigned char*)malloc(total_len);
    if (!bytes) {
        dom_scale_serialized_domain_free(&dom);
        return -5;
    }

    dom_scale_writer_init(&writer, bytes, total_len);
    dom_scale_writer_write_u32(&writer, DOM_SCALE_MACRO_CAPSULE_VERSION);
    dom_scale_writer_write_string(&writer, DOM_SCALE_MACRO_CAPSULE_SCHEMA);
    dom_scale_writer_write_u64(&writer, data->summary.capsule_id);
    dom_scale_writer_write_u64(&writer, data->summary.domain_id);
    dom_scale_writer_write_u32(&writer, data->summary.domain_kind);
    dom_scale_writer_write_i64(&writer, data->summary.source_tick);
    dom_scale_writer_write_u32(&writer, data->summary.collapse_reason);
    dom_scale_writer_write_u32(&writer, data->summary.seed_base);
    dom_scale_writer_write_u64(&writer, invariant_hash);
    dom_scale_writer_write_u64(&writer, statistic_hash);
    dom_scale_writer_write_string_list(&writer, g_scale_invariant_ids, invariant_id_count);
    dom_scale_writer_write_string_list(&writer, stat_ids, stat_id_count);
    dom_scale_writer_write_u32(&writer, (u32)extension_len);
    if (dom.domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        dom_scale_write_resources_payload(&writer, dom.resources, dom.resource_count);
    } else if (dom.domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        dom_scale_write_network_payload(&writer, dom.nodes, dom.node_count, dom.edges, dom.edge_count);
    } else if (dom.domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        dom_scale_write_agents_payload(&writer,
                                       dom.agents,
                                       dom.agent_count,
                                       dom.role_trait,
                                       dom.role_trait_count,
                                       dom.planning,
                                       dom.planning_count);
    }
    dom_scale_extensions_write(&writer, data);
    if (!writer.failed && writer.used != total_len) {
        writer.failed = 1;
    }
    dom_scale_serialized_domain_free(&dom);
    if (writer.failed) {
        free(bytes);
        return -6;
    }

    data->invariant_hash = invariant_hash;
    data->statistic_hash = statistic_hash;
    data->invariant_count = invariant_id_count;
    data->statistic_count = stat_id_count;
    data->summary.invariant_hash = invariant_hash;
    data->summary.statistic_hash = statistic_hash;
    data->summary.invariant_count = invariant_id_count;
    data->summary.statistic_count = stat_id_count;

    *out_bytes = bytes;
    *out_byte_count = (u32)writer.used;
    if (out_invariant_hash) {
        *out_invariant_hash = invariant_hash;
    }
    if (out_statistic_hash) {
        *out_statistic_hash = statistic_hash;
    }
    if (out_invariant_count) {
        *out_invariant_count = invariant_id_count;
    }
    if (out_statistic_count) {
        *out_statistic_count = stat_id_count;
    }
    return 0;
}

static int dom_scale_capsule_parse(const unsigned char* bytes,
                                   u32 byte_count,
                                   dom_scale_capsule_data* out_data)
{
    dom_scale_reader reader;
    u32 version = 0u;
    u32 extension_len = 0u;
    u32 invariant_count = 0u;
    u32 statistic_count = 0u;
    if (!bytes || byte_count == 0u || !out_data) {
        return 0;
    }
    dom_scale_capsule_data_init(out_data);
    dom_scale_reader_init(&reader, bytes, (size_t)byte_count);
    if (!dom_scale_reader_read_u32(&reader, &version)) {
        return 0;
    }
    if (version != DOM_SCALE_MACRO_CAPSULE_VERSION) {
        return 0;
    }
    if (!dom_scale_reader_read_string(&reader,
                                      out_data->schema,
                                      sizeof(out_data->schema),
                                      &out_data->schema_len)) {
        return 0;
    }
    if (!dom_scale_reader_read_u64(&reader, &out_data->summary.capsule_id) ||
        !dom_scale_reader_read_u64(&reader, &out_data->summary.domain_id) ||
        !dom_scale_reader_read_u32(&reader, &out_data->summary.domain_kind) ||
        !dom_scale_reader_read_i64(&reader, &out_data->summary.source_tick) ||
        !dom_scale_reader_read_u32(&reader, &out_data->summary.collapse_reason) ||
        !dom_scale_reader_read_u32(&reader, &out_data->summary.seed_base) ||
        !dom_scale_reader_read_u64(&reader, &out_data->invariant_hash) ||
        !dom_scale_reader_read_u64(&reader, &out_data->statistic_hash)) {
        dom_scale_capsule_data_free(out_data);
        return 0;
    }
    if (!dom_scale_reader_skip_string_list(&reader, &invariant_count) ||
        !dom_scale_reader_skip_string_list(&reader, &statistic_count) ||
        !dom_scale_reader_read_u32(&reader, &extension_len)) {
        dom_scale_capsule_data_free(out_data);
        return 0;
    }
    out_data->invariant_count = invariant_count;
    out_data->statistic_count = statistic_count;
    if (out_data->summary.domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        u32 count = 0u;
        u32 i;
        if (!dom_scale_reader_read_u32(&reader, &count)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->resources = (dom_scale_resource_entry*)malloc(sizeof(dom_scale_resource_entry) * (size_t)(count ? count : 1u));
        if (!out_data->resources) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->resource_count = count;
        for (i = 0u; i < count; ++i) {
            if (!dom_scale_reader_read_u64(&reader, &out_data->resources[i].resource_id) ||
                !dom_scale_reader_read_u64(&reader, &out_data->resources[i].quantity)) {
                dom_scale_capsule_data_free(out_data);
                return 0;
            }
        }
        if (!dom_scale_reader_read_u64(&reader, &out_data->resource_bucket0) ||
            !dom_scale_reader_read_u64(&reader, &out_data->resource_bucket1) ||
            !dom_scale_reader_read_u64(&reader, &out_data->resource_bucket2) ||
            !dom_scale_reader_read_u64(&reader, &out_data->resource_bucket3) ||
            !dom_scale_reader_read_u64(&reader, &out_data->resource_total_qty)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        dom_scale_resource_sort(out_data->resources, count);
    } else if (out_data->summary.domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        u32 node_count = 0u;
        u32 edge_count = 0u;
        u32 i;
        if (!dom_scale_reader_read_u32(&reader, &node_count)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->nodes = (dom_scale_network_node*)malloc(sizeof(dom_scale_network_node) * (size_t)(node_count ? node_count : 1u));
        if (!out_data->nodes) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->node_count = node_count;
        for (i = 0u; i < node_count; ++i) {
            if (!dom_scale_reader_read_u64(&reader, &out_data->nodes[i].node_id) ||
                !dom_scale_reader_read_u32(&reader, &out_data->nodes[i].node_kind)) {
                dom_scale_capsule_data_free(out_data);
                return 0;
            }
        }
        if (!dom_scale_reader_read_u32(&reader, &edge_count)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->edges = (dom_scale_network_edge*)malloc(sizeof(dom_scale_network_edge) * (size_t)(edge_count ? edge_count : 1u));
        if (!out_data->edges) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->edge_count = edge_count;
        for (i = 0u; i < edge_count; ++i) {
            if (!dom_scale_reader_read_u64(&reader, &out_data->edges[i].edge_id) ||
                !dom_scale_reader_read_u64(&reader, &out_data->edges[i].from_node_id) ||
                !dom_scale_reader_read_u64(&reader, &out_data->edges[i].to_node_id) ||
                !dom_scale_reader_read_u64(&reader, &out_data->edges[i].capacity_units) ||
                !dom_scale_reader_read_u64(&reader, &out_data->edges[i].buffer_units) ||
                !dom_scale_reader_read_u32(&reader, &out_data->edges[i].wear_bucket0) ||
                !dom_scale_reader_read_u32(&reader, &out_data->edges[i].wear_bucket1) ||
                !dom_scale_reader_read_u32(&reader, &out_data->edges[i].wear_bucket2) ||
                !dom_scale_reader_read_u32(&reader, &out_data->edges[i].wear_bucket3)) {
                dom_scale_capsule_data_free(out_data);
                return 0;
            }
        }
        if (!dom_scale_reader_read_u32(&reader, &out_data->wear_bucket0) ||
            !dom_scale_reader_read_u32(&reader, &out_data->wear_bucket1) ||
            !dom_scale_reader_read_u32(&reader, &out_data->wear_bucket2) ||
            !dom_scale_reader_read_u32(&reader, &out_data->wear_bucket3) ||
            !dom_scale_reader_read_u32(&reader, &out_data->wear_mean) ||
            !dom_scale_reader_read_u32(&reader, &out_data->wear_p95)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        dom_scale_node_sort(out_data->nodes, node_count);
        dom_scale_edge_sort(out_data->edges, edge_count);
    } else if (out_data->summary.domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        u32 agent_count = 0u;
        u32 role_trait_count = 0u;
        u32 planning_count = 0u;
        size_t skip_len = 0u;
        u32 i;
        if (!dom_scale_reader_read_u32(&reader, &agent_count)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->agents = (dom_scale_agent_entry*)malloc(sizeof(dom_scale_agent_entry) * (size_t)(agent_count ? agent_count : 1u));
        if (!out_data->agents) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        out_data->agent_count = agent_count;
        for (i = 0u; i < agent_count; ++i) {
            if (!dom_scale_reader_read_u64(&reader, &out_data->agents[i].agent_id) ||
                !dom_scale_reader_read_u32(&reader, &out_data->agents[i].role_id) ||
                !dom_scale_reader_read_u32(&reader, &out_data->agents[i].trait_mask) ||
                !dom_scale_reader_read_u32(&reader, &out_data->agents[i].planning_bucket)) {
                dom_scale_capsule_data_free(out_data);
                return 0;
            }
        }
        dom_scale_agent_sort(out_data->agents, agent_count);
        if (!dom_scale_reader_read_u32(&reader, &role_trait_count)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        skip_len = (size_t)role_trait_count * 12u;
        if (!dom_scale_reader_skip(&reader, skip_len)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        if (!dom_scale_reader_read_u32(&reader, &planning_count)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
        skip_len = (size_t)planning_count * 8u;
        if (!dom_scale_reader_skip(&reader, skip_len)) {
            dom_scale_capsule_data_free(out_data);
            return 0;
        }
    } else {
        dom_scale_capsule_data_free(out_data);
        return 0;
    }
    if ((size_t)extension_len > reader.size - reader.pos) {
        dom_scale_capsule_data_free(out_data);
        return 0;
    }
    if (!dom_scale_extensions_parse(out_data, reader.bytes + reader.pos, extension_len)) {
        dom_scale_capsule_data_free(out_data);
        return 0;
    }
    {
        u64 rng_state = 0u;
        if (dom_scale_extensions_get_u64(out_data,
                                         g_scale_rng_state_ext_agents_reconstruct,
                                         &rng_state) &&
            rng_state <= 0xFFFFFFFFu) {
            out_data->rng_state_agents_reconstruct = (u32)rng_state;
            out_data->rng_state_agents_present = 1;
        }
    }
    if (!dom_scale_reader_skip(&reader, (size_t)extension_len)) {
        dom_scale_capsule_data_free(out_data);
        return 0;
    }
    out_data->summary.invariant_hash = out_data->invariant_hash;
    out_data->summary.statistic_hash = out_data->statistic_hash;
    out_data->summary.invariant_count = out_data->invariant_count;
    out_data->summary.statistic_count = out_data->statistic_count;
    return reader.failed ? 0 : 1;
}

static int dom_scale_wear_within_tolerance(const dom_scale_capsule_data* data,
                                           const dom_scale_network_edge* edges,
                                           u32 edge_count)
{
    u32 b0 = 0u;
    u32 b1 = 0u;
    u32 b2 = 0u;
    u32 b3 = 0u;
    u32 mean = 0u;
    u32 p95 = 0u;
    u32 mean_diff;
    u32 p95_diff;
    u32 mean_allow;
    u32 p95_allow;
    if (!data) {
        return 0;
    }
    dom_scale_wear_distribution(edges, edge_count, &b0, &b1, &b2, &b3, &mean, &p95);
    if (b0 != data->wear_bucket0 ||
        b1 != data->wear_bucket1 ||
        b2 != data->wear_bucket2 ||
        b3 != data->wear_bucket3) {
        return 0;
    }
    mean_diff = (mean > data->wear_mean) ? (mean - data->wear_mean) : (data->wear_mean - mean);
    p95_diff = (p95 > data->wear_p95) ? (p95 - data->wear_p95) : (data->wear_p95 - p95);
    mean_allow = data->wear_mean / 100u;
    if (mean_allow < 1u) {
        mean_allow = 1u;
    }
    p95_allow = data->wear_p95 / 100u;
    if (p95_allow < 1u) {
        p95_allow = 1u;
    }
    if (mean_diff > mean_allow) {
        return 0;
    }
    if (p95_diff > p95_allow) {
        return 0;
    }
    return 1;
}

int dom_scale_capsule_summarize(const unsigned char* bytes,
                                u32 byte_count,
                                dom_scale_capsule_summary* out_summary)
{
    dom_scale_capsule_data data;
    if (!out_summary) {
        return -1;
    }
    memset(out_summary, 0, sizeof(*out_summary));
    dom_scale_capsule_data_init(&data);
    if (!dom_scale_capsule_parse(bytes, byte_count, &data)) {
        dom_scale_capsule_data_free(&data);
        return -2;
    }
    *out_summary = data.summary;
    dom_scale_capsule_data_free(&data);
    return 0;
}

static void dom_scale_macro_policy_resolve(const dom_scale_macro_policy* policy,
                                           dom_scale_macro_policy* out_policy)
{
    if (!out_policy) {
        return;
    }
    dom_scale_macro_policy_default(out_policy);
    if (!policy) {
        return;
    }
    if (policy->macro_interval_ticks > 0) {
        out_policy->macro_interval_ticks = policy->macro_interval_ticks;
    }
    if (policy->macro_event_kind > 0u) {
        out_policy->macro_event_kind = policy->macro_event_kind;
    }
    if (policy->narrative_stride > 0u) {
        out_policy->narrative_stride = policy->narrative_stride;
    }
}

static u64 dom_scale_macro_order_seed(u64 capsule_id,
                                      u64 domain_id,
                                      u32 domain_kind,
                                      u32 collapse_reason)
{
    u64 hash = dom_scale_fnv1a64_init();
    hash = dom_scale_hash_u64(hash, capsule_id);
    hash = dom_scale_hash_u64(hash, domain_id);
    hash = dom_scale_hash_u32(hash, domain_kind);
    hash = dom_scale_hash_u32(hash, collapse_reason);
    return hash;
}

static u64 dom_scale_macro_event_id(u64 domain_id,
                                    u64 capsule_id,
                                    dom_act_time_t event_tick,
                                    u32 event_index,
                                    u32 event_kind)
{
    u64 hash = dom_scale_fnv1a64_init();
    hash = dom_scale_hash_u64(hash, domain_id);
    hash = dom_scale_hash_u64(hash, capsule_id);
    hash = dom_scale_hash_i64(hash, event_tick);
    hash = dom_scale_hash_u32(hash, event_index);
    hash = dom_scale_hash_u32(hash, event_kind);
    if (hash == 0u) {
        hash = 1u;
    }
    return hash;
}

static u64 dom_scale_macro_order_key(u64 seed, u32 event_index, u32 event_kind)
{
    u64 hash = dom_scale_fnv1a64_init();
    hash = dom_scale_hash_u64(hash, seed);
    hash = dom_scale_hash_u32(hash, event_index);
    hash = dom_scale_hash_u32(hash, event_kind);
    return hash;
}

static int dom_scale_macro_domain_has_event(const d_world* world, u64 domain_id)
{
    u32 count;
    u32 i;
    dom_macro_event_entry entry;
    if (!world || domain_id == 0u) {
        return 0;
    }
    count = dom_macro_event_queue_count(world);
    for (i = 0u; i < count; ++i) {
        if (dom_macro_event_queue_get_by_index(world, i, &entry) != 0) {
            continue;
        }
        if (entry.domain_id == domain_id) {
            return 1;
        }
    }
    return 0;
}

static int dom_scale_macro_schedule_event(dom_scale_context* ctx,
                                          const dom_scale_domain_slot* slot,
                                          dom_macro_schedule_entry* schedule,
                                          const dom_scale_macro_policy* policy,
                                          u32 reason_code)
{
    dom_macro_event_entry ev;
    dom_act_time_t interval;
    dom_act_time_t event_tick;
    u32 event_index;
    u64 event_id;
    u64 order_key;
    u32 detail_code = DOM_SCALE_DETAIL_NONE;
    if (!ctx || !ctx->world || !slot || !schedule || !policy) {
        return 0;
    }
    interval = schedule->interval_ticks > 0 ? schedule->interval_ticks : policy->macro_interval_ticks;
    if (interval <= 0) {
        interval = 1;
    }
    schedule->interval_ticks = interval;
    event_tick = schedule->next_event_time;
    if (event_tick <= schedule->last_event_time) {
        event_tick = schedule->last_event_time + interval;
        schedule->next_event_time = event_tick;
    }
    if (!dom_scale_macro_queue_within_limit(ctx, &detail_code)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      slot->domain_id,
                                      slot->domain_kind,
                                      schedule->capsule_id,
                                      DOM_FID_LATENT,
                                      reason_code,
                                      DOM_SCALE_DEFER_MACRO_EVENT,
                                      detail_code ? detail_code : DOM_SCALE_DETAIL_MACRO_QUEUE_LIMIT,
                                      DOM_SCALE_DEFERRED_MACRO_EVENT,
                                      DOM_SCALE_BUDGET_MACRO_EVENT,
                                      0);
        return 0;
    }
    event_index = schedule->executed_events + 1u;
    event_id = dom_scale_macro_event_id(slot->domain_id,
                                        schedule->capsule_id,
                                        event_tick,
                                        event_index,
                                        policy->macro_event_kind);
    order_key = dom_scale_macro_order_key(schedule->order_key_seed,
                                          event_index,
                                          policy->macro_event_kind);
    memset(&ev, 0, sizeof(ev));
    ev.event_id = event_id;
    ev.domain_id = slot->domain_id;
    ev.capsule_id = schedule->capsule_id;
    ev.event_time = event_tick;
    ev.order_key = order_key;
    ev.sequence = event_id;
    ev.event_kind = policy->macro_event_kind;
    ev.flags = (policy->narrative_stride > 0u && (event_index % policy->narrative_stride) == 0u) ? 1u : 0u;
    ev.payload0 = event_index;
    ev.payload1 = reason_code;
    if (dom_macro_event_queue_schedule(ctx->world, &ev) != 0) {
        (void)dom_scale_enqueue_defer(ctx,
                                      slot->domain_id,
                                      slot->domain_kind,
                                      schedule->capsule_id,
                                      DOM_FID_LATENT,
                                      reason_code,
                                      DOM_SCALE_DEFER_MACRO_EVENT,
                                      DOM_SCALE_DETAIL_MACRO_SCHEDULE,
                                      DOM_SCALE_DEFERRED_MACRO_EVENT,
                                      DOM_SCALE_BUDGET_MACRO_EVENT,
                                      0);
        return 0;
    }
    dom_scale_deferred_remove_match(ctx, slot->domain_id, DOM_SCALE_DEFERRED_MACRO_EVENT, reason_code);
    dom_scale_emit_macro_schedule(ctx,
                                  slot->domain_id,
                                  slot->domain_kind,
                                  schedule->capsule_id,
                                  reason_code,
                                  (u32)(schedule->order_key_seed & 0xFFFFFFFFu),
                                  event_index);
    return 1;
}

static void dom_scale_macro_reschedule_missing(dom_scale_context* ctx,
                                               const dom_scale_macro_policy* policy,
                                               dom_act_time_t up_to_tick)
{
    u32 i = 0u;
    if (!ctx || !ctx->world || !policy) {
        return;
    }
    while (i < ctx->budget_state.deferred_count) {
        dom_scale_deferred_op op = ctx->budget_state.deferred_ops[i];
        dom_scale_domain_slot* slot;
        dom_macro_schedule_entry schedule;
        int remove_entry = 0;
        if (op.kind != DOM_SCALE_DEFERRED_MACRO_EVENT) {
            ++i;
            continue;
        }
        slot = dom_scale_find_domain(ctx, op.domain_id);
        if (!slot || slot->capsule_id == 0u || slot->tier != DOM_FID_LATENT) {
            remove_entry = 1;
        } else if (dom_macro_schedule_store_get(ctx->world, op.domain_id, &schedule) != 0) {
            remove_entry = 1;
        } else {
            if (schedule.capsule_id != slot->capsule_id) {
                schedule.capsule_id = slot->capsule_id;
            }
            if (dom_scale_macro_domain_has_event(ctx->world, slot->domain_id)) {
                remove_entry = 1;
            } else if (schedule.next_event_time <= up_to_tick) {
                (void)dom_scale_macro_schedule_event(ctx,
                                                     slot,
                                                     &schedule,
                                                     policy,
                                                     policy->macro_event_kind);
            }
            (void)dom_macro_schedule_store_set(ctx->world, &schedule);
        }
        if (remove_entry) {
            dom_scale_deferred_remove_match(ctx, op.domain_id, op.kind, op.reason_code);
            continue;
        }
        ++i;
    }
}

static int dom_scale_macro_execute_event(dom_scale_context* ctx,
                                         const dom_scale_macro_policy* policy,
                                         const dom_macro_event_entry* ev,
                                         dom_macro_schedule_entry* schedule)
{
    dom_scale_domain_slot* slot;
    dom_macro_capsule_blob blob;
    dom_scale_capsule_data data;
    unsigned char* new_bytes = 0;
    u32 new_size = 0u;
    u32 reason_code;
    u32 detail_code = DOM_SCALE_DETAIL_NONE;
    if (!ctx || !ctx->world || !policy || !ev || !schedule) {
        return 0;
    }
    slot = dom_scale_find_domain(ctx, ev->domain_id);
    if (!slot || slot->capsule_id == 0u || slot->tier != DOM_FID_LATENT) {
        return 0;
    }
    reason_code = policy->macro_event_kind;
    if (!dom_scale_budget_allows_macro_event(ctx, ctx->now_tick)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      slot->domain_id,
                                      slot->domain_kind,
                                      schedule->capsule_id,
                                      DOM_FID_LATENT,
                                      reason_code,
                                      DOM_SCALE_DEFER_MACRO_EVENT,
                                      DOM_SCALE_DETAIL_BUDGET_MACRO_EVENT,
                                      DOM_SCALE_DEFERRED_MACRO_EVENT,
                                      DOM_SCALE_BUDGET_MACRO_EVENT,
                                      0);
        return -1;
    }
    if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS &&
        !dom_scale_budget_allows_planning(ctx)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      slot->domain_id,
                                      slot->domain_kind,
                                      schedule->capsule_id,
                                      DOM_FID_LATENT,
                                      reason_code,
                                      DOM_SCALE_DEFER_MACRO_EVENT,
                                      DOM_SCALE_DETAIL_BUDGET_PLANNING,
                                      DOM_SCALE_DEFERRED_PLANNING,
                                      DOM_SCALE_BUDGET_AGENT_PLANNING,
                                      0);
        return -1;
    }
    if (!dom_scale_budget_allows_snapshot(ctx)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      slot->domain_id,
                                      slot->domain_kind,
                                      schedule->capsule_id,
                                      DOM_FID_LATENT,
                                      reason_code,
                                      DOM_SCALE_DEFER_MACRO_EVENT,
                                      DOM_SCALE_DETAIL_BUDGET_SNAPSHOT,
                                      DOM_SCALE_DEFERRED_SNAPSHOT,
                                      DOM_SCALE_BUDGET_SNAPSHOT,
                                      0);
        return -1;
    }
    dom_scale_budget_consume_macro_event(ctx, ctx->now_tick);
    if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        dom_scale_budget_consume_planning(ctx);
    }
    dom_scale_budget_consume_snapshot(ctx);
    memset(&blob, 0, sizeof(blob));
    dom_scale_capsule_data_init(&data);
    if (!dom_macro_capsule_store_get_blob(ctx->world, schedule->capsule_id, &blob) ||
        !dom_scale_capsule_parse(blob.bytes, blob.byte_count, &data)) {
        dom_scale_emit_refusal(ctx,
                               slot->domain_id,
                               slot->domain_kind,
                               reason_code,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_MACRO_EVENT,
                               0);
        dom_scale_capsule_data_free(&data);
        return 0;
    }
    if (data.summary.domain_kind != slot->domain_kind) {
        dom_scale_emit_refusal(ctx,
                               slot->domain_id,
                               slot->domain_kind,
                               reason_code,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_MACRO_EVENT,
                               0);
        dom_scale_capsule_data_free(&data);
        return 0;
    }
    if (data.extension_len > 0u && !data.extension_parse_ok) {
        dom_scale_emit_refusal(ctx,
                               slot->domain_id,
                               slot->domain_kind,
                               reason_code,
                               DOM_SCALE_REFUSE_CAPABILITY_MISSING,
                               DOM_SCALE_DETAIL_MACRO_EVENT,
                               0);
        dom_scale_capsule_data_free(&data);
        return 0;
    }

    schedule->last_event_time = ev->event_time;
    schedule->executed_events += 1u;
    schedule->compacted_through_time = schedule->last_event_time;
    schedule->next_event_time = schedule->last_event_time + schedule->interval_ticks;
    data.summary.source_tick = schedule->last_event_time;
    data.summary.seed_base = dom_scale_seed_base(data.summary.capsule_id, data.summary.source_tick);

    (void)dom_scale_extensions_ensure_scale1(&data);
    (void)dom_scale_extensions_add_or_update_i64(&data,
                                                 "dominium.scale2.macro_last_tick",
                                                 schedule->last_event_time);
    (void)dom_scale_extensions_add_or_update_u64(&data,
                                                 "dominium.scale2.macro_events",
                                                 schedule->executed_events);
    (void)dom_scale_extensions_add_or_update_i64(&data,
                                                 "dominium.scale2.compacted_through",
                                                 schedule->compacted_through_time);
    (void)dom_scale_extensions_add_or_update_i64(&data,
                                                 "dominium.scale2.macro_interval",
                                                 schedule->interval_ticks);
    if (ev->flags & 1u) {
        schedule->narrative_events += 1u;
        (void)dom_scale_extensions_add_or_update_u64(&data,
                                                     "dominium.scale2.narrative_events",
                                                     schedule->narrative_events);
    }

    detail_code = schedule->executed_events;
    if (dom_scale_serialize_capsule_from_data(&data,
                                              &new_bytes,
                                              &new_size,
                                              0,
                                              0,
                                              0,
                                              0) != 0 ||
        dom_macro_capsule_store_set_blob(ctx->world,
                                         data.summary.capsule_id,
                                         data.summary.domain_id,
                                         data.summary.source_tick,
                                         new_bytes,
                                         new_size) != 0) {
        free(new_bytes);
        dom_scale_emit_refusal(ctx,
                               slot->domain_id,
                               slot->domain_kind,
                               reason_code,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_MACRO_EVENT,
                               0);
        dom_scale_capsule_data_free(&data);
        return 0;
    }
    free(new_bytes);
    dom_scale_emit_macro_execute(ctx,
                                 slot->domain_id,
                                 slot->domain_kind,
                                 data.summary.capsule_id,
                                 schedule->last_event_time,
                                 data.summary.seed_base,
                                 detail_code);
    (void)dom_scale_macro_schedule_event(ctx,
                                         slot,
                                         schedule,
                                         policy,
                                         reason_code);
    (void)dom_macro_schedule_store_set(ctx->world, schedule);
    dom_scale_deferred_remove_match(ctx, slot->domain_id, DOM_SCALE_DEFERRED_MACRO_EVENT, reason_code);
    dom_scale_deferred_remove_match(ctx, slot->domain_id, DOM_SCALE_DEFERRED_PLANNING, reason_code);
    dom_scale_deferred_remove_match(ctx, slot->domain_id, DOM_SCALE_DEFERRED_SNAPSHOT, reason_code);
    dom_scale_capsule_data_free(&data);
    return 1;
}

int dom_scale_macro_initialize(dom_scale_context* ctx,
                               const dom_scale_commit_token* token,
                               u64 domain_id,
                               u64 capsule_id,
                               u32 collapse_reason,
                               const dom_scale_macro_policy* policy)
{
    dom_scale_macro_policy resolved;
    dom_scale_domain_slot* slot;
    dom_macro_schedule_entry schedule;
    dom_act_time_t interval;
    if (!ctx || !ctx->world) {
        return -1;
    }
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               0u,
                               collapse_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               0);
        return 0;
    }
    slot = dom_scale_find_domain(ctx, domain_id);
    if (!slot || slot->capsule_id == 0u || slot->tier != DOM_FID_LATENT) {
        return -2;
    }
    dom_scale_macro_policy_resolve(policy, &resolved);
    interval = resolved.macro_interval_ticks > 0 ? resolved.macro_interval_ticks : 1;
    memset(&schedule, 0, sizeof(schedule));
    schedule.domain_id = domain_id;
    schedule.capsule_id = capsule_id;
    schedule.last_event_time = ctx->now_tick;
    schedule.interval_ticks = interval;
    schedule.next_event_time = ctx->now_tick + interval;
    schedule.order_key_seed = dom_scale_macro_order_seed(capsule_id,
                                                         domain_id,
                                                         slot->domain_kind,
                                                         collapse_reason);
    schedule.executed_events = 0u;
    schedule.narrative_events = 0u;
    schedule.compacted_through_time = ctx->now_tick;
    schedule.compaction_count = 0u;
    (void)dom_macro_event_queue_remove_domain(ctx->world, domain_id);
    if (dom_macro_schedule_store_set(ctx->world, &schedule) != 0) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               slot->domain_kind,
                               collapse_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_MACRO_SCHEDULE,
                               0);
        return 0;
    }
    (void)dom_scale_macro_schedule_event(ctx,
                                         slot,
                                         &schedule,
                                         &resolved,
                                         collapse_reason);
    (void)dom_macro_schedule_store_set(ctx->world, &schedule);
    return 1;
}

int dom_scale_macro_request_reschedule(dom_scale_context* ctx,
                                       const dom_scale_commit_token* token,
                                       u64 domain_id,
                                       u32 reason_code)
{
    dom_scale_macro_policy policy;
    dom_scale_domain_slot* slot;
    dom_macro_schedule_entry schedule;
    if (!ctx || !ctx->world) {
        return -1;
    }
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               0u,
                               reason_code,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               0);
        return 0;
    }
    dom_scale_macro_policy_default(&policy);
    slot = dom_scale_find_domain(ctx, domain_id);
    if (!slot || slot->capsule_id == 0u || slot->tier != DOM_FID_LATENT) {
        return -2;
    }
    if (dom_macro_schedule_store_get(ctx->world, domain_id, &schedule) != 0) {
        return 0;
    }
    (void)dom_macro_event_queue_remove_domain(ctx->world, domain_id);
    if (reason_code == 0u) {
        reason_code = policy.macro_event_kind;
    }
    (void)dom_scale_macro_schedule_event(ctx,
                                         slot,
                                         &schedule,
                                         &policy,
                                         reason_code);
    (void)dom_macro_schedule_store_set(ctx->world, &schedule);
    return 1;
}

int dom_scale_macro_advance(dom_scale_context* ctx,
                            const dom_scale_commit_token* token,
                            dom_act_time_t up_to_tick,
                            const dom_scale_macro_policy* policy,
                            u32* out_executed)
{
    dom_scale_macro_policy resolved;
    dom_macro_event_entry ev;
    u32 executed = 0u;
    int budget_blocked = 0;
    if (out_executed) {
        *out_executed = 0u;
    }
    if (!ctx || !ctx->world) {
        return -1;
    }
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               0u,
                               0u,
                               0u,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               0);
        return 0;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    dom_scale_macro_policy_resolve(policy, &resolved);
    dom_scale_macro_reschedule_missing(ctx, &resolved, up_to_tick);
    memset(&ev, 0, sizeof(ev));
    while (dom_macro_event_queue_peek_next(ctx->world, &ev) &&
           ev.event_time <= up_to_tick) {
        dom_macro_schedule_entry schedule;
        int pop_ok;
        if (!dom_macro_event_queue_pop_next(ctx->world, up_to_tick, &ev)) {
            break;
        }
        if (dom_macro_schedule_store_get(ctx->world, ev.domain_id, &schedule) != 0) {
            continue;
        }
        pop_ok = dom_scale_macro_execute_event(ctx, &resolved, &ev, &schedule);
        if (pop_ok < 0) {
            (void)dom_macro_event_queue_schedule(ctx->world, &ev);
            budget_blocked = 1;
            break;
        }
        if (pop_ok > 0) {
            executed += 1u;
        }
    }
    if (out_executed) {
        *out_executed = executed;
    }
    (void)budget_blocked;
    return 0;
}

int dom_scale_macro_compact(dom_scale_context* ctx,
                            const dom_scale_commit_token* token,
                            u64 domain_id,
                            dom_act_time_t up_to_tick,
                            const dom_scale_macro_policy* policy,
                            u32* out_compacted)
{
    dom_scale_macro_policy resolved;
    dom_scale_domain_slot* slot;
    dom_macro_schedule_entry schedule;
    u32 reason_code = 0u;
    int triggered = 0;
    if (out_compacted) {
        *out_compacted = 0u;
    }
    if (!ctx || !ctx->world) {
        return -1;
    }
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               0u,
                               0u,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               0);
        return 0;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    slot = dom_scale_find_domain(ctx, domain_id);
    if (!slot || slot->capsule_id == 0u || slot->tier != DOM_FID_LATENT) {
        return -2;
    }
    if (dom_macro_schedule_store_get(ctx->world, domain_id, &schedule) != 0) {
        return 0;
    }
    dom_scale_macro_policy_resolve(policy, &resolved);
    reason_code = resolved.macro_event_kind;
    if ((ctx->budget_policy.compaction_event_threshold > 0u &&
         schedule.executed_events >= ctx->budget_policy.compaction_event_threshold) ||
        (ctx->budget_policy.compaction_time_threshold > 0 &&
         up_to_tick - schedule.last_event_time >= ctx->budget_policy.compaction_time_threshold)) {
        triggered = 1;
    }
    if (!triggered) {
        return 0;
    }
    if (!dom_scale_budget_allows_compaction(ctx, ctx->now_tick)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      domain_id,
                                      slot->domain_kind,
                                      schedule.capsule_id,
                                      DOM_FID_LATENT,
                                      reason_code,
                                      DOM_SCALE_DEFER_COMPACTION,
                                      DOM_SCALE_DETAIL_BUDGET_COMPACTION,
                                      DOM_SCALE_DEFERRED_SNAPSHOT,
                                      DOM_SCALE_BUDGET_COLLAPSE,
                                      0);
        return 0;
    }
    if (!dom_scale_budget_allows_snapshot(ctx)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      domain_id,
                                      slot->domain_kind,
                                      schedule.capsule_id,
                                      DOM_FID_LATENT,
                                      reason_code,
                                      DOM_SCALE_DEFER_COMPACTION,
                                      DOM_SCALE_DETAIL_BUDGET_SNAPSHOT,
                                      DOM_SCALE_DEFERRED_SNAPSHOT,
                                      DOM_SCALE_BUDGET_SNAPSHOT,
                                      0);
        return 0;
    }
    dom_scale_budget_consume_compaction(ctx, ctx->now_tick);
    dom_scale_budget_consume_snapshot(ctx);
    (void)dom_macro_event_queue_remove_domain(ctx->world, domain_id);
    (void)dom_scale_macro_schedule_event(ctx,
                                         slot,
                                         &schedule,
                                         &resolved,
                                         reason_code);
    (void)dom_macro_schedule_store_set(ctx->world, &schedule);
    dom_scale_emit_macro_compact(ctx,
                                 domain_id,
                                 slot->domain_kind,
                                 schedule.capsule_id,
                                 up_to_tick,
                                 (u32)(schedule.order_key_seed & 0xFFFFFFFFu),
                                 schedule.executed_events);
    if (out_compacted) {
        *out_compacted = 1u;
    }
    return 1;
}

int dom_scale_macro_finalize_for_expand(dom_scale_context* ctx,
                                        const dom_scale_commit_token* token,
                                        u64 domain_id,
                                        dom_act_time_t up_to_tick,
                                        const dom_scale_macro_policy* policy)
{
    dom_scale_macro_policy resolved;
    dom_scale_domain_slot* slot;
    dom_macro_event_entry next_event;
    if (!ctx || !ctx->world) {
        return -1;
    }
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               0u,
                               0u,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               0);
        return 0;
    }
    slot = dom_scale_find_domain(ctx, domain_id);
    if (!slot || slot->capsule_id == 0u) {
        return -2;
    }
    dom_scale_macro_policy_resolve(policy, &resolved);
    (void)dom_scale_macro_advance(ctx, token, up_to_tick, &resolved, 0);
    memset(&next_event, 0, sizeof(next_event));
    if (dom_macro_event_queue_peek_next(ctx->world, &next_event) &&
        next_event.event_time <= up_to_tick) {
        (void)dom_scale_enqueue_defer(ctx,
                                      domain_id,
                                      slot->domain_kind,
                                      slot->capsule_id,
                                      DOM_FID_MICRO,
                                      resolved.macro_event_kind,
                                      DOM_SCALE_DEFER_EXPAND,
                                      DOM_SCALE_DETAIL_BUDGET_MACRO_EVENT,
                                      DOM_SCALE_DEFERRED_EXPAND,
                                      DOM_SCALE_BUDGET_MACRO_EVENT,
                                      0);
        return 0;
    }
    (void)dom_scale_macro_compact(ctx, token, domain_id, up_to_tick, &resolved, 0);
    return 1;
}

static int dom_scale_reconstruct_resources(dom_scale_domain_slot* slot,
                                           const dom_scale_capsule_data* data)
{
    dom_scale_resource_entry* temp = 0;
    u32 count;
    if (!slot || !data) {
        return 0;
    }
    count = data->resource_count;
    if (count > slot->resources.capacity) {
        return 0;
    }
    temp = (dom_scale_resource_entry*)malloc(sizeof(dom_scale_resource_entry) * (size_t)(count ? count : 1u));
    if (!temp) {
        return 0;
    }
    if (count > 0u) {
        memcpy(temp, data->resources, sizeof(dom_scale_resource_entry) * (size_t)count);
        dom_scale_resource_sort(temp, count);
        memcpy(slot->resources.entries, temp, sizeof(dom_scale_resource_entry) * (size_t)count);
    }
    slot->resources.count = count;
    free(temp);
    return 1;
}

static int dom_scale_reconstruct_network(dom_scale_domain_slot* slot,
                                         const dom_scale_capsule_data* data)
{
    dom_scale_network_node* nodes = 0;
    dom_scale_network_edge* edges = 0;
    u32 node_count;
    u32 edge_count;
    if (!slot || !data) {
        return 0;
    }
    node_count = data->node_count;
    edge_count = data->edge_count;
    if (node_count > slot->network.node_capacity ||
        edge_count > slot->network.edge_capacity) {
        return 0;
    }
    nodes = (dom_scale_network_node*)malloc(sizeof(dom_scale_network_node) * (size_t)(node_count ? node_count : 1u));
    edges = (dom_scale_network_edge*)malloc(sizeof(dom_scale_network_edge) * (size_t)(edge_count ? edge_count : 1u));
    if (!nodes || !edges) {
        free(nodes);
        free(edges);
        return 0;
    }
    if (node_count > 0u) {
        memcpy(nodes, data->nodes, sizeof(dom_scale_network_node) * (size_t)node_count);
        dom_scale_node_sort(nodes, node_count);
        memcpy(slot->network.nodes, nodes, sizeof(dom_scale_network_node) * (size_t)node_count);
    }
    if (edge_count > 0u) {
        memcpy(edges, data->edges, sizeof(dom_scale_network_edge) * (size_t)edge_count);
        dom_scale_edge_sort(edges, edge_count);
        memcpy(slot->network.edges, edges, sizeof(dom_scale_network_edge) * (size_t)edge_count);
    }
    slot->network.node_count = node_count;
    slot->network.edge_count = edge_count;
    free(nodes);
    free(edges);
    return 1;
}

static int dom_scale_reconstruct_agents(dom_scale_domain_slot* slot,
                                        const dom_scale_capsule_data* data,
                                        dom_scale_context* ctx)
{
    dom_scale_agent_entry* temp = 0;
    u32 count;
    u32 i;
    if (!slot || !data || !ctx) {
        return 0;
    }
    count = data->agent_count;
    if (count > slot->agents.capacity) {
        return 0;
    }
    temp = (dom_scale_agent_entry*)malloc(sizeof(dom_scale_agent_entry) * (size_t)(count ? count : 1u));
    if (!temp) {
        return 0;
    }
    if (count > 0u && data->agents) {
        memcpy(temp, data->agents, sizeof(dom_scale_agent_entry) * (size_t)count);
    } else if (count > 0u) {
        d_rng_state rng;
        u32 seed = data->summary.seed_base ? data->summary.seed_base
                                           : dom_scale_seed_base(data->summary.capsule_id, ctx->now_tick);
        D_DET_GUARD_RNG_STREAM_NAME(g_scale_rng_stream_agents_reconstruct);
        if (data->rng_state_agents_present) {
            rng.state = data->rng_state_agents_reconstruct ? data->rng_state_agents_reconstruct : 1u;
        } else {
            rng.state = dom_scale_rng_state_from_seed(seed,
                                                      slot->domain_id,
                                                      g_scale_rng_stream_agents_reconstruct);
        }
        for (i = 0u; i < count; ++i) {
            u32 r = d_rng_next_u32(&rng);
            temp[i].agent_id = ((slot->domain_id & 0xFFFFFFFFull) << 32) ^ (u64)(r ^ (i + 1u));
            temp[i].role_id = 0u;
            temp[i].trait_mask = 0u;
            temp[i].planning_bucket = 0u;
        }
    }
    if (count > 0u) {
        dom_scale_agent_sort(temp, count);
        memcpy(slot->agents.entries, temp, sizeof(dom_scale_agent_entry) * (size_t)count);
    }
    slot->agents.count = count;
    free(temp);
    return 1;
}

int dom_scale_collapse_domain(dom_scale_context* ctx,
                              const dom_scale_commit_token* token,
                              u64 domain_id,
                              u32 collapse_reason,
                              dom_scale_operation_result* out_result)
{
    dom_scale_domain_slot* slot;
    dom_interest_state* interest_state;
    unsigned char* capsule_bytes = 0;
    u32 capsule_size = 0u;
    u64 capsule_id = 0u;
    u32 seed_base = 0u;
    u64 invariant_hash = 0u;
    u64 statistic_hash = 0u;
    u32 invariant_count = 0u;
    u32 statistic_count = 0u;
    u64 hash_before = 0u;
    u64 hash_after = 0u;
    u64 capsule_hash = 0u;
    dom_fidelity_tier from_tier = DOM_FID_LATENT;
    dom_fidelity_tier to_tier = DOM_FID_LATENT;

    if (!ctx) {
        return -1;
    }
    slot = dom_scale_find_domain(ctx, domain_id);
    if (!slot) {
        return -2;
    }
    dom_scale_result_init(out_result, domain_id, slot->domain_kind, ctx->now_tick);
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    from_tier = slot->tier;
    if (out_result) {
        out_result->from_tier = from_tier;
    }
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               slot->domain_kind,
                               collapse_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               out_result);
        return 0;
    }
    if (!dom_scale_domain_supported(slot->domain_kind)) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               slot->domain_kind,
                               collapse_reason,
                               DOM_SCALE_REFUSE_CAPABILITY_MISSING,
                               DOM_SCALE_DETAIL_DOMAIN_UNSUPPORTED,
                               out_result);
        return 0;
    }
    interest_state = dom_scale_find_interest_state(ctx, domain_id);
    if (interest_state && interest_state->state == DOM_REL_HOT) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               slot->domain_kind,
                               collapse_reason,
                               DOM_SCALE_REFUSE_DOMAIN_FORBIDDEN,
                               DOM_SCALE_DETAIL_INTEREST_TIER2,
                               out_result);
        return 0;
    }
    if (!dom_scale_dwell_elapsed(ctx->now_tick,
                                 slot->last_transition_tick,
                                 ctx->budget_policy.min_dwell_ticks)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      domain_id,
                                      slot->domain_kind,
                                      slot->capsule_id,
                                      DOM_FID_LATENT,
                                      collapse_reason,
                                      DOM_SCALE_DEFER_COLLAPSE,
                                      DOM_SCALE_DETAIL_DWELL_TICKS,
                                      DOM_SCALE_DEFERRED_COLLAPSE,
                                      DOM_SCALE_BUDGET_NONE,
                                      out_result);
        return 0;
    }
    if (!dom_scale_budget_allows_collapse(ctx)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      domain_id,
                                      slot->domain_kind,
                                      slot->capsule_id,
                                      DOM_FID_LATENT,
                                      collapse_reason,
                                      DOM_SCALE_DEFER_COLLAPSE,
                                      DOM_SCALE_DETAIL_BUDGET_COLLAPSE,
                                      DOM_SCALE_DEFERRED_COLLAPSE,
                                      DOM_SCALE_BUDGET_COLLAPSE,
                                      out_result);
        return 0;
    }
    if (!dom_scale_budget_allows_snapshot(ctx)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      domain_id,
                                      slot->domain_kind,
                                      slot->capsule_id,
                                      DOM_FID_LATENT,
                                      collapse_reason,
                                      DOM_SCALE_DEFER_COLLAPSE,
                                      DOM_SCALE_DETAIL_BUDGET_SNAPSHOT,
                                      DOM_SCALE_DEFERRED_SNAPSHOT,
                                      DOM_SCALE_BUDGET_SNAPSHOT,
                                      out_result);
        return 0;
    }

    dom_scale_budget_consume_collapse(ctx);
    dom_scale_budget_consume_snapshot(ctx);
    hash_before = dom_scale_domain_hash(slot, ctx->now_tick, ctx->worker_count);
    capsule_id = dom_scale_capsule_id(domain_id, slot->domain_kind, ctx->now_tick, collapse_reason);
    seed_base = dom_scale_seed_base(capsule_id, ctx->now_tick);

    if (dom_scale_serialize_capsule(slot,
                                    ctx->now_tick,
                                    collapse_reason,
                                    capsule_id,
                                    seed_base,
                                    &capsule_bytes,
                                    &capsule_size,
                                    &invariant_hash,
                                    &statistic_hash,
                                    &invariant_count,
                                    &statistic_count) != 0) {
        dom_scale_emit_refusal(ctx,
                               domain_id,
                               slot->domain_kind,
                               collapse_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_CAPSULE_PARSE,
                               out_result);
        free(capsule_bytes);
        return 0;
    }
    capsule_hash = dom_scale_capsule_hash(capsule_bytes, capsule_size);
    if (ctx->world) {
        (void)dom_macro_capsule_store_set_blob(ctx->world,
                                               capsule_id,
                                               domain_id,
                                               ctx->now_tick,
                                               capsule_bytes,
                                               capsule_size);
    }
    slot->capsule_id = capsule_id;
    to_tier = DOM_FID_LATENT;
    slot->tier = to_tier;
    slot->last_transition_tick = ctx->now_tick;
    dom_scale_budget_adjust_for_transition(ctx, from_tier, to_tier);
    hash_after = dom_scale_domain_hash(slot, ctx->now_tick, ctx->worker_count);
    if (ctx->world) {
        dom_scale_macro_policy macro_policy;
        dom_scale_macro_policy_default(&macro_policy);
        (void)dom_scale_macro_initialize(ctx,
                                         token,
                                         domain_id,
                                         capsule_id,
                                         collapse_reason,
                                         &macro_policy);
    }
    dom_scale_deferred_remove_match(ctx, domain_id, DOM_SCALE_DEFERRED_COLLAPSE, collapse_reason);
    dom_scale_deferred_remove_match(ctx, domain_id, DOM_SCALE_DEFERRED_SNAPSHOT, collapse_reason);

    if (out_result) {
        out_result->capsule_id = capsule_id;
        out_result->to_tier = to_tier;
        out_result->reason_code = collapse_reason;
        out_result->domain_hash_before = hash_before;
        out_result->domain_hash_after = hash_after;
        out_result->capsule_hash = capsule_hash;
    }
    dom_scale_emit_collapse(ctx,
                            domain_id,
                            slot->domain_kind,
                            capsule_id,
                            collapse_reason,
                            seed_base);
    free(capsule_bytes);
    (void)invariant_hash;
    (void)statistic_hash;
    (void)invariant_count;
    (void)statistic_count;
    return 0;
}

int dom_scale_expand_domain(dom_scale_context* ctx,
                            const dom_scale_commit_token* token,
                            u64 capsule_id,
                            dom_fidelity_tier target_tier,
                            u32 expand_reason,
                            dom_scale_operation_result* out_result)
{
    dom_macro_capsule_blob blob;
    dom_scale_capsule_data data;
    dom_scale_macro_policy macro_policy;
    dom_scale_domain_slot* slot = 0;
    dom_fidelity_tier from_tier = DOM_FID_LATENT;
    dom_fidelity_tier to_tier = target_tier;
    u64 capsule_hash = 0u;

    if (!ctx || !ctx->world) {
        return -1;
    }
    dom_scale_budget_begin_tick(ctx, ctx->now_tick);
    memset(&blob, 0, sizeof(blob));
    dom_scale_capsule_data_init(&data);
    dom_scale_macro_policy_default(&macro_policy);
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               0u,
                               0u,
                               expand_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               out_result);
        return 0;
    }
    if (!dom_macro_capsule_store_get_blob(ctx->world, capsule_id, &blob)) {
        dom_scale_emit_refusal(ctx,
                               0u,
                               0u,
                               expand_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_CAPSULE_PARSE,
                               out_result);
        return 0;
    }
    if (!dom_scale_macro_finalize_for_expand(ctx,
                                             token,
                                             blob.domain_id,
                                             ctx->now_tick,
                                             &macro_policy)) {
        return 0;
    }
    if (!dom_macro_capsule_store_get_blob(ctx->world, capsule_id, &blob)) {
        dom_scale_emit_refusal(ctx,
                               0u,
                               0u,
                               expand_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_CAPSULE_PARSE,
                               out_result);
        return 0;
    }
    capsule_hash = dom_scale_capsule_hash(blob.bytes, blob.byte_count);
    if (!dom_scale_capsule_parse(blob.bytes, blob.byte_count, &data)) {
        dom_scale_emit_refusal(ctx,
                               blob.domain_id,
                               0u,
                               expand_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_CAPSULE_PARSE,
                               out_result);
        dom_scale_capsule_data_free(&data);
        return 0;
    }
    slot = dom_scale_find_domain(ctx, data.summary.domain_id);
    if (!slot) {
        dom_scale_emit_refusal(ctx,
                               data.summary.domain_id,
                               data.summary.domain_kind,
                               expand_reason,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_CAPSULE_PARSE,
                               out_result);
        dom_scale_capsule_data_free(&data);
        return 0;
    }
    dom_scale_result_init(out_result, slot->domain_id, slot->domain_kind, ctx->now_tick);
    from_tier = slot->tier;
    if (out_result) {
        out_result->from_tier = from_tier;
    }
    if (!dom_scale_domain_supported(slot->domain_kind) ||
        slot->domain_kind != data.summary.domain_kind) {
        dom_scale_emit_refusal(ctx,
                               slot->domain_id,
                               slot->domain_kind,
                               expand_reason,
                               DOM_SCALE_REFUSE_CAPABILITY_MISSING,
                               DOM_SCALE_DETAIL_DOMAIN_UNSUPPORTED,
                               out_result);
        dom_scale_capsule_data_free(&data);
        return 0;
    }
    if (!dom_scale_dwell_elapsed(ctx->now_tick,
                                 slot->last_transition_tick,
                                 ctx->budget_policy.min_dwell_ticks)) {
        (void)dom_scale_enqueue_defer(ctx,
                                      slot->domain_id,
                                      slot->domain_kind,
                                      capsule_id,
                                      target_tier,
                                      expand_reason,
                                      DOM_SCALE_DEFER_EXPAND,
                                      DOM_SCALE_DETAIL_DWELL_TICKS,
                                      DOM_SCALE_DEFERRED_EXPAND,
                                      DOM_SCALE_BUDGET_NONE,
                                      out_result);
        dom_scale_capsule_data_free(&data);
        return 0;
    }

    return dom_scale_expand_apply(ctx,
                                  slot,
                                  data,
                                  from_tier,
                                  to_tier,
                                  expand_reason,
                                  capsule_id,
                                  capsule_hash,
                                  out_result);
}

static dom_fidelity_tier dom_scale_target_tier_from_relevance(dom_relevance_state state)
{
    if (state == DOM_REL_HOT) {
        return DOM_FID_MICRO;
    }
    if (state == DOM_REL_WARM) {
        return DOM_FID_MESO;
    }
    return DOM_FID_LATENT;
}

static int dom_scale_transition_cmp(const dom_interest_transition* a,
                                    const dom_interest_transition* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->target_id < b->target_id) return -1;
    if (a->target_id > b->target_id) return 1;
    if (a->to_state < b->to_state) return -1;
    if (a->to_state > b->to_state) return 1;
    if (a->from_state < b->from_state) return -1;
    if (a->from_state > b->from_state) return 1;
    return 0;
}

static void dom_scale_transition_sort(dom_interest_transition* transitions, u32 count)
{
    u32 i;
    if (!transitions) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_interest_transition key = transitions[i];
        u32 j = i;
        while (j > 0u && dom_scale_transition_cmp(&transitions[j - 1u], &key) > 0) {
            transitions[j] = transitions[j - 1u];
            --j;
        }
        transitions[j] = key;
    }
}

u32 dom_scale_apply_interest(dom_scale_context* ctx,
                             const dom_scale_commit_token* token,
                             const dom_interest_set* interest,
                             dom_scale_operation_result* out_results,
                             u32 result_capacity)
{
    dom_interest_transition* transitions = 0;
    u32 transition_cap = 0u;
    u32 i;
    u32 written = 0u;
    if (!ctx || !interest || !ctx->interest_states) {
        return 0u;
    }
    if (!dom_scale_commit_token_validate(token, ctx->now_tick)) {
        dom_scale_emit_refusal(ctx,
                               0u,
                               0u,
                               0u,
                               DOM_SCALE_REFUSE_INVALID_INTENT,
                               DOM_SCALE_DETAIL_COMMIT_TICK,
                               0);
        return 0u;
    }
    transition_cap = ctx->domain_count;
    if (transition_cap == 0u) {
        return 0u;
    }
    transitions = (dom_interest_transition*)malloc(sizeof(dom_interest_transition) * (size_t)transition_cap);
    if (!transitions) {
        return 0u;
    }
    memset(transitions, 0, sizeof(dom_interest_transition) * (size_t)transition_cap);
    (void)dom_interest_state_apply(interest,
                                   ctx->interest_states,
                                   ctx->domain_count,
                                   &ctx->interest_policy,
                                   ctx->now_tick,
                                   transitions,
                                   &transition_cap);
    dom_scale_transition_sort(transitions, transition_cap);
    for (i = 0u; i < transition_cap; ++i) {
        dom_interest_transition* tr = &transitions[i];
        dom_scale_domain_slot* slot = dom_scale_find_domain(ctx, tr->target_id);
        dom_fidelity_tier target_tier;
        dom_scale_operation_result* res = (out_results && written < result_capacity)
                                              ? &out_results[written]
                                              : 0;
        if (!slot) {
            continue;
        }
        target_tier = dom_scale_target_tier_from_relevance(tr->to_state);
        if (target_tier == DOM_FID_LATENT && slot->tier != DOM_FID_LATENT) {
            (void)dom_scale_collapse_domain(ctx,
                                            token,
                                            slot->domain_id,
                                            tr->to_state,
                                            res);
            written += 1u;
        } else if (target_tier != DOM_FID_LATENT && slot->capsule_id != 0u) {
            (void)dom_scale_expand_domain(ctx,
                                          token,
                                          slot->capsule_id,
                                          target_tier,
                                          tr->to_state,
                                          res);
            written += 1u;
        }
    }
    free(transitions);
    return written;
}

const char* dom_scale_refusal_to_string(u32 refusal_code)
{
    switch (refusal_code) {
    case DOM_SCALE_REFUSE_INVALID_INTENT: return "REFUSE_INVALID_INTENT";
    case DOM_SCALE_REFUSE_CAPABILITY_MISSING: return "REFUSE_CAPABILITY_MISSING";
    case DOM_SCALE_REFUSE_DOMAIN_FORBIDDEN: return "REFUSE_DOMAIN_FORBIDDEN";
    case DOM_SCALE_REFUSE_BUDGET_EXCEEDED: return "REFUSE_BUDGET_EXCEEDED";
    case DOM_SCALE_REFUSE_ACTIVE_DOMAIN_LIMIT: return "REFUSE_ACTIVE_DOMAIN_LIMIT";
    case DOM_SCALE_REFUSE_REFINEMENT_BUDGET: return "REFUSE_REFINEMENT_BUDGET";
    case DOM_SCALE_REFUSE_MACRO_EVENT_BUDGET: return "REFUSE_MACRO_EVENT_BUDGET";
    case DOM_SCALE_REFUSE_AGENT_PLANNING_BUDGET: return "REFUSE_AGENT_PLANNING_BUDGET";
    case DOM_SCALE_REFUSE_SNAPSHOT_BUDGET: return "REFUSE_SNAPSHOT_BUDGET";
    case DOM_SCALE_REFUSE_COLLAPSE_BUDGET: return "REFUSE_COLLAPSE_BUDGET";
    case DOM_SCALE_REFUSE_DEFER_QUEUE_LIMIT: return "REFUSE_DEFER_QUEUE_LIMIT";
    default: break;
    }
    return "REFUSE_NONE";
}

const char* dom_scale_defer_to_string(u32 defer_code)
{
    switch (defer_code) {
    case DOM_SCALE_DEFER_COLLAPSE: return "DEFER_COLLAPSE";
    case DOM_SCALE_DEFER_EXPAND: return "DEFER_EXPANSION";
    case DOM_SCALE_DEFER_MACRO_EVENT: return "DEFER_MACRO_EVENT";
    case DOM_SCALE_DEFER_COMPACTION: return "DEFER_COMPACTION";
    default: break;
    }
    return "DEFER_NONE";
}

void dom_scale_budget_snapshot_current(const dom_scale_context* ctx,
                                       dom_scale_budget_snapshot* out_snapshot)
{
    if (!out_snapshot) {
        return;
    }
    memset(out_snapshot, 0, sizeof(*out_snapshot));
    if (!ctx) {
        return;
    }
    out_snapshot->tick = ctx->now_tick;
    out_snapshot->active_tier1_domains = ctx->budget_state.active_tier1_domains;
    out_snapshot->active_tier2_domains = ctx->budget_state.active_tier2_domains;
    out_snapshot->tier1_limit = ctx->budget_policy.max_tier1_domains;
    out_snapshot->tier2_limit = dom_scale_policy_tier2_limit(&ctx->budget_policy);
    out_snapshot->refinement_used = ctx->budget_state.refinement_used;
    out_snapshot->refinement_limit = ctx->budget_policy.refinement_budget_per_tick;
    out_snapshot->planning_used = ctx->budget_state.planning_used;
    out_snapshot->planning_limit = ctx->budget_policy.planning_budget_per_tick;
    out_snapshot->collapse_used = ctx->budget_state.collapse_used;
    out_snapshot->collapse_limit = ctx->budget_policy.collapse_budget_per_tick;
    out_snapshot->expand_used = ctx->budget_state.expand_used;
    out_snapshot->expand_limit = ctx->budget_policy.expand_budget_per_tick;
    out_snapshot->macro_event_used = ctx->budget_state.macro_event_used;
    out_snapshot->macro_event_limit = ctx->budget_policy.macro_event_budget_per_tick;
    out_snapshot->snapshot_used = ctx->budget_state.snapshot_used;
    out_snapshot->snapshot_limit = ctx->budget_policy.snapshot_budget_per_tick;
    out_snapshot->deferred_count = ctx->budget_state.deferred_count;
    out_snapshot->deferred_overflow = ctx->budget_state.deferred_overflow;
    out_snapshot->deferred_limit = dom_scale_policy_deferred_limit(&ctx->budget_policy);
    out_snapshot->refusal_active_domain_limit = ctx->budget_state.refusal_active_domain_limit;
    out_snapshot->refusal_refinement_budget = ctx->budget_state.refusal_refinement_budget;
    out_snapshot->refusal_macro_event_budget = ctx->budget_state.refusal_macro_event_budget;
    out_snapshot->refusal_agent_planning_budget = ctx->budget_state.refusal_agent_planning_budget;
    out_snapshot->refusal_snapshot_budget = ctx->budget_state.refusal_snapshot_budget;
    out_snapshot->refusal_collapse_budget = ctx->budget_state.refusal_collapse_budget;
    out_snapshot->refusal_defer_queue_limit = ctx->budget_state.refusal_defer_queue_limit;
}

u32 dom_scale_deferred_count(const dom_scale_context* ctx)
{
    if (!ctx) {
        return 0u;
    }
    return ctx->budget_state.deferred_count;
}

int dom_scale_deferred_get(const dom_scale_context* ctx,
                           u32 index,
                           dom_scale_deferred_op* out_op)
{
    if (!ctx || index >= ctx->budget_state.deferred_count) {
        return 0;
    }
    if (out_op) {
        *out_op = ctx->budget_state.deferred_ops[index];
    }
    return 1;
}

void dom_scale_deferred_clear(dom_scale_context* ctx)
{
    if (!ctx) {
        return;
    }
    ctx->budget_state.deferred_count = 0u;
    ctx->budget_state.deferred_overflow = 0u;
    memset(ctx->budget_state.deferred_ops, 0, sizeof(ctx->budget_state.deferred_ops));
}

static int dom_scale_expand_apply(dom_scale_context* ctx,
                                  dom_scale_domain_slot* slot,
                                  dom_scale_capsule_data data,
                                  dom_fidelity_tier from_tier,
                                  dom_fidelity_tier to_tier,
                                  u32 expand_reason,
                                  u64 capsule_id,
                                  u64 capsule_hash,
                                  dom_scale_operation_result* out_result)
{
    u32 budget_detail = DOM_SCALE_DETAIL_NONE;
    u32 saved_tier1 = 0u;
    u32 saved_tier2 = 0u;
    u64 hash_before = 0u;
    u64 hash_after = 0u;

    saved_tier1 = ctx->budget_state.active_tier1_domains;
    saved_tier2 = ctx->budget_state.active_tier2_domains;
    if (dom_scale_is_tier2(from_tier) && ctx->budget_state.active_tier2_domains > 0u) {
        ctx->budget_state.active_tier2_domains -= 1u;
    } else if (dom_scale_is_tier1(from_tier) && ctx->budget_state.active_tier1_domains > 0u) {
        ctx->budget_state.active_tier1_domains -= 1u;
    }
    if (!dom_scale_budget_allows_expand(ctx, to_tier, &budget_detail)) {
        u32 refusal_code = DOM_SCALE_REFUSE_BUDGET_EXCEEDED;
        if (budget_detail == DOM_SCALE_DETAIL_ACTIVE_DOMAIN_LIMIT ||
            budget_detail == DOM_SCALE_DETAIL_TIER_CAP) {
            refusal_code = DOM_SCALE_REFUSE_ACTIVE_DOMAIN_LIMIT;
        } else if (budget_detail == DOM_SCALE_DETAIL_BUDGET_REFINEMENT ||
                   budget_detail == DOM_SCALE_DETAIL_BUDGET_EXPAND) {
            refusal_code = DOM_SCALE_REFUSE_REFINEMENT_BUDGET;
        }
        ctx->budget_state.active_tier1_domains = saved_tier1;
        ctx->budget_state.active_tier2_domains = saved_tier2;
        dom_scale_emit_refusal(ctx,
                               slot->domain_id,
                               slot->domain_kind,
                               expand_reason,
                               refusal_code,
                               budget_detail ? budget_detail : DOM_SCALE_DETAIL_BUDGET_EXPAND,
                               out_result);
        dom_scale_capsule_data_free(&data);
        return 0;
    }
    ctx->budget_state.active_tier1_domains = saved_tier1;
    ctx->budget_state.active_tier2_domains = saved_tier2;

    dom_scale_budget_consume_refinement(ctx);
    dom_scale_budget_consume_expand(ctx);
    hash_before = dom_scale_domain_hash(slot, ctx->now_tick, ctx->worker_count);

    if (slot->domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        dom_scale_domain_slot temp_slot = *slot;
        dom_scale_resource_entry* temp_entries = 0;
        u64 inv_hash = 0u;
        u64 stat_hash = 0u;
        u32 count = data.resource_count;
        temp_entries = (dom_scale_resource_entry*)malloc(sizeof(dom_scale_resource_entry) * (size_t)(count ? count : 1u));
        if (!temp_entries) {
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        temp_slot.resources.entries = temp_entries;
        temp_slot.resources.capacity = count;
        temp_slot.resources.count = 0u;
        if (!dom_scale_reconstruct_resources(&temp_slot, &data)) {
            free(temp_entries);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        inv_hash = dom_scale_resource_invariant_hash(temp_slot.resources.entries,
                                                     temp_slot.resources.count,
                                                     data.summary.source_tick);
        stat_hash = dom_scale_resource_stat_hash(temp_slot.resources.entries,
                                                 temp_slot.resources.count);
        if ((data.invariant_hash && inv_hash != data.invariant_hash) ||
            (data.statistic_hash && stat_hash != data.statistic_hash)) {
            free(temp_entries);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_INVARIANT_MISMATCH,
                                   out_result);
            return 0;
        }
        if (temp_slot.resources.count > slot->resources.capacity) {
            free(temp_entries);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        if (temp_slot.resources.count > 0u) {
            memcpy(slot->resources.entries,
                   temp_slot.resources.entries,
                   sizeof(dom_scale_resource_entry) * (size_t)temp_slot.resources.count);
        }
        slot->resources.count = temp_slot.resources.count;
        free(temp_entries);
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        dom_scale_domain_slot temp_slot = *slot;
        dom_scale_network_node* temp_nodes = 0;
        dom_scale_network_edge* temp_edges = 0;
        u64 inv_hash = 0u;
        u64 stat_hash = 0u;
        u32 node_count = data.node_count;
        u32 edge_count = data.edge_count;
        temp_nodes = (dom_scale_network_node*)malloc(sizeof(dom_scale_network_node) * (size_t)(node_count ? node_count : 1u));
        temp_edges = (dom_scale_network_edge*)malloc(sizeof(dom_scale_network_edge) * (size_t)(edge_count ? edge_count : 1u));
        if (!temp_nodes || !temp_edges) {
            free(temp_nodes);
            free(temp_edges);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        temp_slot.network.nodes = temp_nodes;
        temp_slot.network.node_capacity = node_count;
        temp_slot.network.node_count = 0u;
        temp_slot.network.edges = temp_edges;
        temp_slot.network.edge_capacity = edge_count;
        temp_slot.network.edge_count = 0u;
        if (!dom_scale_reconstruct_network(&temp_slot, &data)) {
            free(temp_nodes);
            free(temp_edges);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        inv_hash = dom_scale_network_invariant_hash(temp_slot.network.nodes,
                                                    temp_slot.network.node_count,
                                                    temp_slot.network.edges,
                                                    temp_slot.network.edge_count,
                                                    data.summary.source_tick);
        stat_hash = dom_scale_network_stat_hash(temp_slot.network.edges,
                                                temp_slot.network.edge_count);
        if ((data.invariant_hash && inv_hash != data.invariant_hash) ||
            (data.statistic_hash && stat_hash != data.statistic_hash) ||
            !dom_scale_wear_within_tolerance(&data,
                                             temp_slot.network.edges,
                                             temp_slot.network.edge_count)) {
            free(temp_nodes);
            free(temp_edges);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_INVARIANT_MISMATCH,
                                   out_result);
            return 0;
        }
        if (temp_slot.network.node_count > slot->network.node_capacity ||
            temp_slot.network.edge_count > slot->network.edge_capacity) {
            free(temp_nodes);
            free(temp_edges);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        if (temp_slot.network.node_count > 0u) {
            memcpy(slot->network.nodes,
                   temp_slot.network.nodes,
                   sizeof(dom_scale_network_node) * (size_t)temp_slot.network.node_count);
        }
        if (temp_slot.network.edge_count > 0u) {
            memcpy(slot->network.edges,
                   temp_slot.network.edges,
                   sizeof(dom_scale_network_edge) * (size_t)temp_slot.network.edge_count);
        }
        slot->network.node_count = temp_slot.network.node_count;
        slot->network.edge_count = temp_slot.network.edge_count;
        free(temp_nodes);
        free(temp_edges);
    } else if (slot->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        dom_scale_domain_slot temp_slot = *slot;
        dom_scale_agent_entry* temp_agents = 0;
        u64 inv_hash = 0u;
        u64 stat_hash = 0u;
        u32 count = data.agent_count;
        if (!dom_scale_budget_allows_planning(ctx)) {
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_AGENT_PLANNING_BUDGET,
                                   DOM_SCALE_DETAIL_BUDGET_PLANNING,
                                   out_result);
            return 0;
        }
        dom_scale_budget_consume_planning(ctx);
        temp_agents = (dom_scale_agent_entry*)malloc(sizeof(dom_scale_agent_entry) * (size_t)(count ? count : 1u));
        if (!temp_agents) {
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        temp_slot.agents.entries = temp_agents;
        temp_slot.agents.capacity = count;
        temp_slot.agents.count = 0u;
        if (!dom_scale_reconstruct_agents(&temp_slot, &data, ctx)) {
            free(temp_agents);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        inv_hash = dom_scale_agent_invariant_hash(temp_slot.agents.entries,
                                                  temp_slot.agents.count,
                                                  data.summary.source_tick);
        stat_hash = dom_scale_agent_stat_hash(temp_slot.agents.entries,
                                              temp_slot.agents.count);
        if ((data.invariant_hash && inv_hash != data.invariant_hash) ||
            (data.statistic_hash && stat_hash != data.statistic_hash)) {
            free(temp_agents);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_INVARIANT_MISMATCH,
                                   out_result);
            return 0;
        }
        if (temp_slot.agents.count > slot->agents.capacity) {
            free(temp_agents);
            dom_scale_capsule_data_free(&data);
            dom_scale_emit_refusal(ctx,
                                   slot->domain_id,
                                   slot->domain_kind,
                                   expand_reason,
                                   DOM_SCALE_REFUSE_INVALID_INTENT,
                                   DOM_SCALE_DETAIL_CAPACITY,
                                   out_result);
            return 0;
        }
        if (temp_slot.agents.count > 0u) {
            memcpy(slot->agents.entries,
                   temp_slot.agents.entries,
                   sizeof(dom_scale_agent_entry) * (size_t)temp_slot.agents.count);
        }
        slot->agents.count = temp_slot.agents.count;
        free(temp_agents);
    }

    slot->capsule_id = capsule_id;
    slot->tier = to_tier;
    slot->last_transition_tick = ctx->now_tick;
    dom_scale_budget_adjust_for_transition(ctx, from_tier, to_tier);
    hash_after = dom_scale_domain_hash(slot, ctx->now_tick, ctx->worker_count);
    if (ctx->world) {
        (void)dom_macro_event_queue_remove_domain(ctx->world, slot->domain_id);
        (void)dom_macro_schedule_store_remove(ctx->world, slot->domain_id);
    }
    dom_scale_deferred_remove_match(ctx, slot->domain_id, DOM_SCALE_DEFERRED_EXPAND, expand_reason);
    dom_scale_deferred_remove_match(ctx, slot->domain_id, DOM_SCALE_DEFERRED_PLANNING, expand_reason);
    dom_scale_deferred_remove_match(ctx, slot->domain_id, DOM_SCALE_DEFERRED_SNAPSHOT, expand_reason);

    if (out_result) {
        out_result->capsule_id = capsule_id;
        out_result->to_tier = to_tier;
        out_result->reason_code = expand_reason;
        out_result->domain_hash_before = hash_before;
        out_result->domain_hash_after = hash_after;
        out_result->capsule_hash = capsule_hash;
    }
    dom_scale_emit_expand(ctx,
                          slot->domain_id,
                          slot->domain_kind,
                          capsule_id,
                          expand_reason,
                          data.summary.seed_base);
    dom_scale_capsule_data_free(&data);
    return 0;
}
