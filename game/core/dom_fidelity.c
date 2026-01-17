/*
FILE: game/core/dom_fidelity.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / fidelity
RESPONSIBILITY: Implements fidelity state tracking and refine/collapse request processing.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and transitions are mandatory.
*/
#include "dominium/fidelity.h"

#include <string.h>

int dom_fidelity_context_init(dom_fidelity_context* ctx,
                              dom_fidelity_object* object_storage,
                              u32 object_capacity,
                              dom_fidelity_request* request_storage,
                              u32 request_capacity)
{
    if (!ctx || !object_storage || !request_storage) {
        return -1;
    }
    ctx->objects = object_storage;
    ctx->object_capacity = object_capacity;
    ctx->object_count = 0u;
    ctx->requests = request_storage;
    ctx->request_capacity = request_capacity;
    ctx->request_count = 0u;
    memset(ctx->objects, 0, sizeof(dom_fidelity_object) * (size_t)object_capacity);
    memset(ctx->requests, 0, sizeof(dom_fidelity_request) * (size_t)request_capacity);
    return 0;
}

static int dom_fidelity_object_matches(const dom_fidelity_object* obj, u32 kind, u64 id)
{
    return obj && obj->object_kind == kind && obj->object_id == id;
}

dom_fidelity_object* dom_fidelity_register_object(dom_fidelity_context* ctx,
                                                  u32 object_kind,
                                                  u64 object_id,
                                                  dom_fidelity_tier tier)
{
    u32 i;
    if (!ctx || !ctx->objects) {
        return NULL;
    }
    for (i = 0u; i < ctx->object_count; ++i) {
        if (dom_fidelity_object_matches(&ctx->objects[i], object_kind, object_id)) {
            return &ctx->objects[i];
        }
    }
    if (ctx->object_count >= ctx->object_capacity) {
        return NULL;
    }
    ctx->objects[ctx->object_count].object_kind = object_kind;
    ctx->objects[ctx->object_count].object_id = object_id;
    ctx->objects[ctx->object_count].state.current_tier = tier;
    ctx->objects[ctx->object_count].state.last_transition_tick = 0;
    ctx->objects[ctx->object_count].state.pin_flags = 0u;
    ctx->objects[ctx->object_count].state.provenance_summary_hash = 0u;
    ctx->objects[ctx->object_count].count = 0u;
    ctx->objects[ctx->object_count].inventory = 0u;
    ctx->objects[ctx->object_count].obligations = 0u;
    ctx->object_count += 1u;
    return &ctx->objects[ctx->object_count - 1u];
}

dom_fidelity_object* dom_fidelity_find_object(dom_fidelity_context* ctx,
                                              u32 object_kind,
                                              u64 object_id)
{
    u32 i;
    if (!ctx || !ctx->objects) {
        return NULL;
    }
    for (i = 0u; i < ctx->object_count; ++i) {
        if (dom_fidelity_object_matches(&ctx->objects[i], object_kind, object_id)) {
            return &ctx->objects[i];
        }
    }
    return NULL;
}

void dom_fidelity_set_pins(dom_fidelity_object* obj, u32 pin_flags)
{
    if (!obj) {
        return;
    }
    obj->state.pin_flags = pin_flags;
}

void dom_fidelity_set_provenance_hash(dom_fidelity_object* obj, u64 hash)
{
    if (!obj) {
        return;
    }
    obj->state.provenance_summary_hash = hash;
}

static int dom_fidelity_request_add(dom_fidelity_context* ctx,
                                    u32 object_kind,
                                    u64 object_id,
                                    dom_fidelity_request_type type,
                                    dom_fidelity_tier target_tier,
                                    u32 reason)
{
    dom_fidelity_request* req;
    if (!ctx || !ctx->requests) {
        return -1;
    }
    if (ctx->request_count >= ctx->request_capacity) {
        return -2;
    }
    req = &ctx->requests[ctx->request_count++];
    req->object_kind = object_kind;
    req->object_id = object_id;
    req->type = type;
    req->target_tier = target_tier;
    req->reason = reason;
    return 0;
}

int dom_fidelity_request_refine(dom_fidelity_context* ctx,
                                u32 object_kind,
                                u64 object_id,
                                dom_fidelity_tier target_tier,
                                u32 reason)
{
    return dom_fidelity_request_add(ctx, object_kind, object_id, DOM_FIDELITY_REQUEST_REFINE, target_tier, reason);
}

int dom_fidelity_request_collapse(dom_fidelity_context* ctx,
                                  u32 object_kind,
                                  u64 object_id,
                                  dom_fidelity_tier target_tier,
                                  u32 reason)
{
    return dom_fidelity_request_add(ctx, object_kind, object_id, DOM_FIDELITY_REQUEST_COLLAPSE, target_tier, reason);
}

static int dom_fidelity_request_cmp(const dom_fidelity_request* a, const dom_fidelity_request* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->object_kind < b->object_kind) return -1;
    if (a->object_kind > b->object_kind) return 1;
    if (a->object_id < b->object_id) return -1;
    if (a->object_id > b->object_id) return 1;
    if (a->type < b->type) return -1;
    if (a->type > b->type) return 1;
    if (a->target_tier < b->target_tier) return -1;
    if (a->target_tier > b->target_tier) return 1;
    if (a->reason < b->reason) return -1;
    if (a->reason > b->reason) return 1;
    return 0;
}

static void dom_fidelity_request_sort(dom_fidelity_request* reqs, u32 count)
{
    u32 i;
    if (!reqs) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_fidelity_request key = reqs[i];
        u32 j = i;
        while (j > 0u && dom_fidelity_request_cmp(&reqs[j - 1u], &key) > 0) {
            reqs[j] = reqs[j - 1u];
            --j;
        }
        reqs[j] = key;
    }
}

static int dom_fidelity_provenance_ok(const dom_fidelity_object* obj)
{
    return obj && obj->state.provenance_summary_hash != 0u;
}

static int dom_fidelity_can_collapse(const dom_fidelity_object* obj,
                                     const dom_interest_set* interest,
                                     const dom_fidelity_policy* policy,
                                     dom_act_time_t now_tick)
{
    u32 strength;
    if (!obj) {
        return 0;
    }
    if (obj->state.pin_flags & DOM_FIDELITY_PIN_VISIBLE) {
        return 0;
    }
    if (policy && policy->min_dwell_ticks > 0) {
        dom_act_time_t elapsed = now_tick - obj->state.last_transition_tick;
        if (elapsed < policy->min_dwell_ticks) {
            return 0;
        }
    }
    strength = dom_interest_set_strength(interest, obj->object_kind, obj->object_id, now_tick, NULL);
    if (policy) {
        return strength <= policy->collapse_max_strength;
    }
    return strength == 0u;
}

static int dom_fidelity_can_refine(const dom_fidelity_object* obj,
                                   const dom_interest_set* interest,
                                   const dom_fidelity_policy* policy,
                                   dom_act_time_t now_tick)
{
    u32 strength;
    if (!obj || !interest) {
        return 0;
    }
    if (policy && policy->min_dwell_ticks > 0) {
        dom_act_time_t elapsed = now_tick - obj->state.last_transition_tick;
        if (elapsed < policy->min_dwell_ticks) {
            return 0;
        }
    }
    strength = dom_interest_set_strength(interest, obj->object_kind, obj->object_id, now_tick, NULL);
    if (policy) {
        return strength >= policy->refine_min_strength;
    }
    return strength > 0u;
}

u32 dom_fidelity_apply_requests(dom_fidelity_context* ctx,
                                const dom_interest_set* interest,
                                const dom_fidelity_policy* policy,
                                dom_act_time_t now_tick,
                                dom_fidelity_transition* out_transitions,
                                u32* in_out_transition_count)
{
    u32 i;
    u32 written = 0u;
    u32 max_out = in_out_transition_count ? *in_out_transition_count : 0u;
    dom_fidelity_policy local_policy;

    if (!ctx || !ctx->requests) {
        return 0u;
    }
    if (!policy) {
        local_policy.refine_min_strength = 1u;
        local_policy.collapse_max_strength = 0u;
        local_policy.min_dwell_ticks = 0;
        policy = &local_policy;
    }

    dom_fidelity_request_sort(ctx->requests, ctx->request_count);

    for (i = 0u; i < ctx->request_count; ++i) {
        const dom_fidelity_request* req = &ctx->requests[i];
        dom_fidelity_object* obj = dom_fidelity_find_object(ctx, req->object_kind, req->object_id);
        dom_fidelity_tier from_tier;
        if (!obj) {
            continue;
        }
        from_tier = obj->state.current_tier;
        if (from_tier == req->target_tier) {
            continue;
        }
        if (!dom_fidelity_provenance_ok(obj)) {
            continue;
        }
        if (req->type == DOM_FIDELITY_REQUEST_COLLAPSE) {
            if (req->target_tier < DOM_FIDELITY_MICRO &&
                (obj->state.pin_flags & DOM_FIDELITY_PIN_VISIBLE)) {
                continue;
            }
            if (!dom_fidelity_can_collapse(obj, interest, policy, now_tick)) {
                continue;
            }
        } else if (req->type == DOM_FIDELITY_REQUEST_REFINE) {
            if (!dom_fidelity_can_refine(obj, interest, policy, now_tick)) {
                continue;
            }
        } else {
            continue;
        }

        obj->state.current_tier = req->target_tier;
        obj->state.last_transition_tick = now_tick;
        if (out_transitions && written < max_out) {
            out_transitions[written].object_id = obj->object_id;
            out_transitions[written].object_kind = obj->object_kind;
            out_transitions[written].from_tier = from_tier;
            out_transitions[written].to_tier = req->target_tier;
        }
        written += 1u;
    }

    ctx->request_count = 0u;
    if (in_out_transition_count) {
        *in_out_transition_count = written > max_out ? max_out : written;
    }
    return written;
}
