/*
FILE: game/rules/scale/world_streaming_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Work IR-based world streaming emission (derived tasks only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Emission order and plan comparison are deterministic.
*/
#include "dominium/rules/scale/world_streaming_system.h"

#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"


enum {
    DOM_STREAMING_COMPONENT_CACHE = 5001u,
    DOM_STREAMING_FIELD_STATUS = 1u
};

static u32 dom_streaming_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u64 dom_streaming_fnv1a64(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_streaming_task_fidelity(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_LATENT: return DOM_FID_LATENT;
        case DOM_FIDELITY_MACRO: return DOM_FID_MACRO;
        case DOM_FIDELITY_MESO: return DOM_FID_MESO;
        case DOM_FIDELITY_MICRO: return DOM_FID_MICRO;
        case DOM_FIDELITY_FOCUS: return DOM_FID_FOCUS;
        default: return DOM_FID_LATENT;
    }
}

static u32 dom_streaming_strength_threshold(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS:
        case DOM_FIDELITY_MICRO:
            return DOM_INTEREST_STRENGTH_LOW;
        case DOM_FIDELITY_MESO:
            return DOM_INTEREST_STRENGTH_MED;
        case DOM_FIDELITY_MACRO:
            return DOM_INTEREST_STRENGTH_HIGH;
        case DOM_FIDELITY_LATENT:
        default:
            return 101u;
    }
}

static u32 dom_streaming_max_tasks(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS: return 8u;
        case DOM_FIDELITY_MICRO: return 6u;
        case DOM_FIDELITY_MESO: return 4u;
        case DOM_FIDELITY_MACRO: return 2u;
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

static d_bool dom_streaming_allow_unload(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS:
        case DOM_FIDELITY_MICRO:
        case DOM_FIDELITY_MESO:
            return D_TRUE;
        case DOM_FIDELITY_MACRO:
        case DOM_FIDELITY_LATENT:
        default:
            return D_FALSE;
    }
}

static d_bool dom_streaming_cache_contains(const dom_streaming_cache* cache, u64 chunk_id)
{
    u32 lo = 0u;
    u32 hi;
    if (!cache || !cache->loaded_chunk_ids || cache->loaded_count == 0u) {
        return D_FALSE;
    }
    hi = cache->loaded_count;
    while (lo < hi) {
        u32 mid = lo + (hi - lo) / 2u;
        u64 value = cache->loaded_chunk_ids[mid];
        if (value == chunk_id) {
            return D_TRUE;
        }
        if (value < chunk_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return D_FALSE;
}

static d_bool dom_streaming_interest_desired(const dom_interest_set* set,
                                             u64 chunk_id,
                                             u32 threshold,
                                             dom_act_time_t now)
{
    u32 i;
    if (!set || !set->entries) {
        return D_FALSE;
    }
    for (i = 0u; i < set->count; ++i) {
        const dom_interest_entry* entry = &set->entries[i];
        if (entry->target_kind != DOM_INTEREST_TARGET_REGION) {
            continue;
        }
        if (entry->target_id != chunk_id) {
            continue;
        }
        if (entry->expiry_tick != DOM_INTEREST_PERSISTENT && entry->expiry_tick <= now) {
            continue;
        }
        if (entry->strength < threshold) {
            continue;
        }
        return D_TRUE;
    }
    return D_FALSE;
}

static u32 dom_streaming_emit_plan(const dom_interest_set* set,
                                   const dom_streaming_cache* cache,
                                   dom_act_time_t now,
                                   u32 threshold,
                                   d_bool allow_unload,
                                   dom_streaming_request* out,
                                   u32 out_capacity,
                                   u32 max_tasks)
{
    u32 count = 0u;
    u32 i;
    u64 last_target = 0u;
    d_bool has_last = D_FALSE;

    if (!out || out_capacity == 0u || max_tasks == 0u) {
        return 0u;
    }
    if (!set || !set->entries || set->count == 0u) {
        return 0u;
    }

    for (i = 0u; i < set->count; ++i) {
        const dom_interest_entry* entry = &set->entries[i];
        if (entry->target_kind != DOM_INTEREST_TARGET_REGION) {
            continue;
        }
        if (entry->expiry_tick != DOM_INTEREST_PERSISTENT && entry->expiry_tick <= now) {
            continue;
        }
        if (entry->strength < threshold) {
            continue;
        }
        if (has_last && entry->target_id == last_target) {
            continue;
        }
        last_target = entry->target_id;
        has_last = D_TRUE;
        if (dom_streaming_cache_contains(cache, entry->target_id) == D_TRUE) {
            continue;
        }
        out[count].op = DOM_STREAM_OP_LOAD_CHUNK;
        out[count].chunk_id = entry->target_id;
        count += 1u;
        if (count >= max_tasks || count >= out_capacity) {
            return count;
        }
    }

    if (allow_unload != D_TRUE || !cache || !cache->loaded_chunk_ids) {
        return count;
    }

    for (i = 0u; i < cache->loaded_count; ++i) {
        u64 chunk_id = cache->loaded_chunk_ids[i];
        if (dom_streaming_interest_desired(set, chunk_id, threshold, now) == D_TRUE) {
            continue;
        }
        out[count].op = DOM_STREAM_OP_UNLOAD_CHUNK;
        out[count].chunk_id = chunk_id;
        count += 1u;
        if (count >= max_tasks || count >= out_capacity) {
            return count;
        }
    }

    return count;
}

static d_bool dom_streaming_plan_equal(const dom_streaming_request* a,
                                       u32 count_a,
                                       const dom_streaming_request* b,
                                       u32 count_b)
{
    u32 i;
    if (count_a != count_b) {
        return D_FALSE;
    }
    for (i = 0u; i < count_a; ++i) {
        if (a[i].op != b[i].op || a[i].chunk_id != b[i].chunk_id) {
            return D_FALSE;
        }
    }
    return D_TRUE;
}

WorldStreamingSystem::WorldStreamingSystem()
    : system_id_(0u),
      law_target_count_(0u),
      law_scope_ref_(1u),
      tier_(DOM_FIDELITY_MACRO),
      next_due_tick_(DOM_TIME_ACT_MAX),
      migration_state_(DOM_STREAMING_STATE_DUAL),
      mismatch_count_(0u),
      interest_set_(0),
      interest_set_id_(0u),
      cache_(0),
      ir_requests_(0),
      ir_capacity_(0u),
      ir_count_(0u),
      legacy_requests_(0),
      legacy_capacity_(0u),
      legacy_count_(0u)
{
    system_id_ = dom_streaming_fnv1a64("WORLD_STREAMING");
    law_targets_[0] = dom_streaming_fnv1a32("EXEC.DERIVED_TASK");
    law_targets_[1] = dom_streaming_fnv1a32("WORLD.DATA_ACCESS");
    law_target_count_ = 2u;
}

int WorldStreamingSystem::init(const dom_interest_set* interest_set,
                               const dom_streaming_cache* cache,
                               u64 interest_set_id,
                               dom_streaming_request* ir_storage,
                               u32 ir_capacity,
                               dom_streaming_request* legacy_storage,
                               u32 legacy_capacity)
{
    interest_set_ = interest_set;
    interest_set_id_ = interest_set_id;
    cache_ = cache;
    ir_requests_ = ir_storage;
    ir_capacity_ = ir_capacity;
    legacy_requests_ = legacy_storage;
    legacy_capacity_ = legacy_capacity;
    ir_count_ = 0u;
    legacy_count_ = 0u;
    return 0;
}

void WorldStreamingSystem::set_interest_set(const dom_interest_set* interest_set, u64 interest_set_id)
{
    interest_set_ = interest_set;
    interest_set_id_ = interest_set_id;
}

void WorldStreamingSystem::set_cache(const dom_streaming_cache* cache)
{
    cache_ = cache;
}

void WorldStreamingSystem::set_next_due_tick(dom_act_time_t tick)
{
    next_due_tick_ = tick;
}

void WorldStreamingSystem::set_migration_state(dom_streaming_migration_state state)
{
    migration_state_ = state;
}

dom_streaming_migration_state WorldStreamingSystem::migration_state() const
{
    return migration_state_;
}

u32 WorldStreamingSystem::mismatch_count() const
{
    return mismatch_count_;
}

u64 WorldStreamingSystem::system_id() const
{
    return system_id_;
}

d_bool WorldStreamingSystem::is_sim_affecting() const
{
    return D_FALSE;
}

const u32* WorldStreamingSystem::law_targets(u32* out_count) const
{
    if (out_count) {
        *out_count = law_target_count_;
    }
    return law_targets_;
}

dom_act_time_t WorldStreamingSystem::get_next_due_tick() const
{
    return next_due_tick_;
}

void WorldStreamingSystem::degrade(dom_fidelity_tier tier, u32 reason)
{
    (void)reason;
    tier_ = tier;
}

int WorldStreamingSystem::emit_tasks(dom_act_time_t act_now,
                                     dom_act_time_t act_target,
                                     dom_work_graph_builder* graph_builder,
                                     dom_access_set_builder* access_builder)
{
    u32 i;
    u32 threshold;
    u32 max_tasks;
    d_bool allow_unload;

    (void)act_target;
    if (!graph_builder || !access_builder) {
        return -1;
    }
    if (!interest_set_ || !ir_requests_ || ir_capacity_ == 0u) {
        return 0;
    }

    threshold = dom_streaming_strength_threshold(tier_);
    max_tasks = dom_streaming_max_tasks(tier_);
    allow_unload = dom_streaming_allow_unload(tier_);
    if (budget_hint() > 0u && budget_hint() < max_tasks) {
        max_tasks = budget_hint();
    }
    if (max_tasks > ir_capacity_) {
        max_tasks = ir_capacity_;
    }

    ir_count_ = dom_streaming_emit_plan(interest_set_, cache_, act_now,
                                        threshold, allow_unload,
                                        ir_requests_, ir_capacity_, max_tasks);

    if (migration_state_ == DOM_STREAMING_STATE_DUAL &&
        legacy_requests_ && legacy_capacity_ > 0u) {
        legacy_count_ = dom_streaming_emit_plan(interest_set_, cache_, act_now,
                                                threshold, allow_unload,
                                                legacy_requests_, legacy_capacity_, max_tasks);
        if (dom_streaming_plan_equal(ir_requests_, ir_count_,
                                     legacy_requests_, legacy_count_) == D_FALSE) {
            mismatch_count_ += 1u;
        }
    }

    for (i = 0u; i < ir_count_; ++i) {
        u32 local_id = i + 1u;
        u64 task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        u64 access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        u64 cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);
        dom_task_node node;
        dom_cost_model cost;
        dom_access_range read_interest;
        dom_access_range read_cache;
        dom_access_range write_cache;

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_DERIVED;
        node.determinism_class = DOM_DET_DERIVED;
        node.fidelity_tier = dom_streaming_task_fidelity(tier_);
        node.next_due_tick = DOM_EXEC_TICK_INVALID;
        node.access_set_id = access_id;
        node.cost_model_id = cost_id;
        node.law_targets = law_targets_;
        node.law_target_count = law_target_count_;
        node.phase_id = 0u;
        node.commit_key = dom_work_graph_builder_make_commit_key(0u, task_id, 0u);
        node.law_scope_ref = law_scope_ref_;
        node.actor_ref = 0u;
        node.capability_set_ref = 0u;
        node.policy_params = &ir_requests_[i];
        node.policy_params_size = (u32)sizeof(dom_streaming_request);

        cost.cost_id = cost_id;
        cost.cpu_upper_bound = 1u;
        cost.memory_upper_bound = 1u;
        cost.bandwidth_upper_bound = (ir_requests_[i].op == DOM_STREAM_OP_LOAD_CHUNK) ? 8u : 2u;
        cost.latency_class = DOM_LATENCY_HIGH;
        cost.degradation_priority = 2;

        if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
            return -2;
        }
        if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
            return -3;
        }

        read_interest.kind = DOM_RANGE_INTEREST_SET;
        read_interest.component_id = 0u;
        read_interest.field_id = 0u;
        read_interest.start_id = 0u;
        read_interest.end_id = 0u;
        read_interest.set_id = interest_set_id_;
        if (dom_access_set_builder_add_read(access_builder, &read_interest) != 0) {
            return -4;
        }

        read_cache.kind = DOM_RANGE_SINGLE;
        read_cache.component_id = DOM_STREAMING_COMPONENT_CACHE;
        read_cache.field_id = DOM_STREAMING_FIELD_STATUS;
        read_cache.start_id = ir_requests_[i].chunk_id;
        read_cache.end_id = ir_requests_[i].chunk_id;
        read_cache.set_id = 0u;
        if (dom_access_set_builder_add_read(access_builder, &read_cache) != 0) {
            return -5;
        }

        write_cache.kind = DOM_RANGE_SINGLE;
        write_cache.component_id = DOM_STREAMING_COMPONENT_CACHE;
        write_cache.field_id = DOM_STREAMING_FIELD_STATUS;
        write_cache.start_id = ir_requests_[i].chunk_id;
        write_cache.end_id = ir_requests_[i].chunk_id;
        write_cache.set_id = 0u;
        if (dom_access_set_builder_add_write(access_builder, &write_cache) != 0) {
            return -6;
        }
        if (dom_access_set_builder_finalize(access_builder) != 0) {
            return -7;
        }
        if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
            return -8;
        }
    }
    return 0;
}
