/*
FILE: game/rules/player/player_intent.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / player
RESPONSIBILITY: Implements player intent queues, validation, and feedback events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Intent validation and event ordering are deterministic.
*/
#include "dominium/player.h"

#include <string.h>

void dom_player_registry_init(dom_player_registry* registry,
                              dom_player_record* storage,
                              u32 capacity)
{
    if (!registry) {
        return;
    }
    registry->entries = storage;
    registry->count = 0u;
    registry->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_player_record) * (size_t)capacity);
    }
}

dom_player_record* dom_player_find(dom_player_registry* registry,
                                   dom_player_id player_id)
{
    u32 i;
    if (!registry || !registry->entries) {
        return 0;
    }
    for (i = 0u; i < registry->count; ++i) {
        if (registry->entries[i].player_id == player_id) {
            return &registry->entries[i];
        }
    }
    return 0;
}

int dom_player_bind(dom_player_registry* registry,
                    dom_player_id player_id,
                    u64 agent_id)
{
    dom_player_record* record;
    if (!registry || !registry->entries || player_id == 0u || agent_id == 0u) {
        return -1;
    }
    record = dom_player_find(registry, player_id);
    if (record) {
        record->agent_id = agent_id;
        return 0;
    }
    if (registry->count >= registry->capacity) {
        return -2;
    }
    record = &registry->entries[registry->count++];
    memset(record, 0, sizeof(*record));
    record->player_id = player_id;
    record->agent_id = agent_id;
    record->flags = 0u;
    return 0;
}

void dom_player_intent_queue_init(dom_player_intent_queue* queue,
                                  dom_player_intent* storage,
                                  u32 capacity,
                                  u64 start_id)
{
    if (!queue) {
        return;
    }
    queue->entries = storage;
    queue->count = 0u;
    queue->capacity = capacity;
    queue->next_intent_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_player_intent) * (size_t)capacity);
    }
}

void dom_player_event_log_init(dom_player_event_log* log,
                               dom_player_event* storage,
                               u32 capacity,
                               u64 start_id)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->next_event_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_player_event) * (size_t)capacity);
    }
}

int dom_player_event_record(dom_player_event_log* log,
                            dom_player_id player_id,
                            u64 agent_id,
                            u32 kind,
                            u64 intent_id,
                            u32 refusal,
                            dom_act_time_t act_time)
{
    dom_player_event* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    memset(entry, 0, sizeof(*entry));
    entry->event_id = log->next_event_id++;
    entry->player_id = player_id;
    entry->agent_id = agent_id;
    entry->kind = kind;
    entry->intent_id = intent_id;
    entry->refusal = refusal;
    entry->act_time = act_time;
    return 0;
}

static const dom_agent_belief* dom_player_find_belief(const dom_agent_belief* beliefs,
                                                      u32 belief_count,
                                                      u64 agent_id)
{
    u32 i;
    if (!beliefs) {
        return 0;
    }
    for (i = 0u; i < belief_count; ++i) {
        if (beliefs[i].agent_id == agent_id) {
            return &beliefs[i];
        }
    }
    return 0;
}

static const dom_agent_capability* dom_player_find_cap(const dom_agent_capability* caps,
                                                       u32 cap_count,
                                                       u64 agent_id)
{
    u32 i;
    if (!caps) {
        return 0;
    }
    for (i = 0u; i < cap_count; ++i) {
        if (caps[i].agent_id == agent_id) {
            return &caps[i];
        }
    }
    return 0;
}

int dom_player_build_snapshot(const dom_agent_belief* beliefs,
                              u32 belief_count,
                              u64 agent_id,
                              dom_player_subjective_snapshot* out_snapshot)
{
    const dom_agent_belief* belief;
    if (!out_snapshot) {
        return -1;
    }
    memset(out_snapshot, 0, sizeof(*out_snapshot));
    out_snapshot->agent_id = agent_id;
    belief = dom_player_find_belief(beliefs, belief_count, agent_id);
    if (!belief) {
        return -2;
    }
    out_snapshot->knowledge_mask = belief->knowledge_mask;
    out_snapshot->epistemic_confidence_q16 = belief->epistemic_confidence_q16;
    out_snapshot->known_resource_ref = belief->known_resource_ref;
    out_snapshot->known_threat_ref = belief->known_threat_ref;
    out_snapshot->known_destination_ref = belief->known_destination_ref;
    return 0;
}

static u32 dom_player_effective_authority(const dom_player_intent_context* ctx,
                                          const dom_agent_capability* cap,
                                          u64 agent_id,
                                          dom_act_time_t now_act)
{
    u32 mask = cap ? cap->authority_mask : 0u;
    if (ctx && ctx->authority) {
        mask = agent_authority_effective_mask(ctx->authority, agent_id, mask, now_act);
    }
    return mask;
}

static int dom_player_check_knowledge(const dom_player_intent_context* ctx,
                                      u64 agent_id,
                                      u32 required_knowledge)
{
    const dom_agent_belief* belief;
    if (required_knowledge == 0u) {
        return 1;
    }
    belief = dom_player_find_belief(ctx ? ctx->beliefs : 0,
                                    ctx ? ctx->belief_count : 0u,
                                    agent_id);
    if (!belief) {
        return 0;
    }
    if ((belief->knowledge_mask & required_knowledge) != required_knowledge) {
        return 0;
    }
    return 1;
}

static int dom_player_check_physical(const dom_player_intent_context* ctx,
                                     const dom_player_process_request* req)
{
    i32 slope = 0;
    i32 bearing = 0;
    if (!ctx || !ctx->fields || !req) {
        return 1;
    }
    if (req->max_slope_q16 > 0) {
        if (dom_field_get_value(ctx->fields, DOM_FIELD_SLOPE,
                                req->x, req->y, &slope) == 0) {
            if (slope > req->max_slope_q16) {
                return 0;
            }
        }
    }
    if (req->min_bearing_q16 > 0) {
        if (dom_field_get_value(ctx->fields, DOM_FIELD_BEARING_CAPACITY,
                                req->x, req->y, &bearing) == 0) {
            if (bearing < req->min_bearing_q16) {
                return 0;
            }
        }
    }
    return 1;
}

static int dom_player_enqueue(dom_player_intent_queue* queue,
                              const dom_player_intent* intent)
{
    dom_player_intent* entry;
    if (!queue || !queue->entries || !intent) {
        return -1;
    }
    if (queue->count >= queue->capacity) {
        return -2;
    }
    entry = &queue->entries[queue->count++];
    *entry = *intent;
    return 0;
}

int dom_player_submit_intent(dom_player_intent_queue* queue,
                             const dom_player_intent* intent,
                             const dom_player_intent_context* ctx)
{
    dom_player_intent mutable_intent;
    const dom_agent_capability* cap;
    u32 effective_auth;
    u32 refusal = DOM_PLAYER_REFUSAL_NONE;
    int ok = 1;

    if (!queue || !intent) {
        return -1;
    }
    mutable_intent = *intent;
    mutable_intent.intent_id = queue->next_intent_id++;
    mutable_intent.status = DOM_PLAYER_INTENT_PENDING;
    mutable_intent.refusal = DOM_PLAYER_REFUSAL_NONE;

    cap = dom_player_find_cap(ctx ? ctx->caps : 0, ctx ? ctx->cap_count : 0u,
                              mutable_intent.agent_id);
    effective_auth = dom_player_effective_authority(ctx, cap,
                                                    mutable_intent.agent_id,
                                                    ctx ? ctx->now_act : 0u);

    switch (mutable_intent.kind) {
        case DOM_PLAYER_INTENT_GOAL_UPDATE: {
            agent_goal_desc* desc = &mutable_intent.payload.goal_update.desc;
            if (!cap || (cap->capability_mask & desc->preconditions.required_capabilities) !=
                desc->preconditions.required_capabilities) {
                refusal = DOM_PLAYER_REFUSAL_NO_CAPABILITY;
                ok = 0;
            } else if ((effective_auth & desc->preconditions.required_authority) !=
                       desc->preconditions.required_authority) {
                refusal = DOM_PLAYER_REFUSAL_NO_AUTHORITY;
                ok = 0;
            } else if (!dom_player_check_knowledge(ctx,
                                                   mutable_intent.agent_id,
                                                   desc->preconditions.required_knowledge)) {
                refusal = DOM_PLAYER_REFUSAL_NO_KNOWLEDGE;
                ok = 0;
            }
            if (ok && ctx && ctx->goals) {
                if (agent_goal_register(ctx->goals, desc, 0) != 0) {
                    refusal = DOM_PLAYER_REFUSAL_INVALID_INTENT;
                    ok = 0;
                }
            }
            break;
        }
        case DOM_PLAYER_INTENT_PLAN_CONFIRM:
            if (mutable_intent.payload.plan_id == 0u) {
                refusal = DOM_PLAYER_REFUSAL_PLAN_NOT_FOUND;
                ok = 0;
            }
            break;
        case DOM_PLAYER_INTENT_PROCESS_REQUEST: {
            const dom_player_process_request* req = &mutable_intent.payload.process_request;
            if (!cap || (cap->capability_mask & req->required_capability_mask) !=
                req->required_capability_mask) {
                refusal = DOM_PLAYER_REFUSAL_NO_CAPABILITY;
                ok = 0;
            } else if ((effective_auth & req->required_authority_mask) !=
                       req->required_authority_mask) {
                refusal = DOM_PLAYER_REFUSAL_NO_AUTHORITY;
                ok = 0;
            } else if (!dom_player_check_knowledge(ctx,
                                                   mutable_intent.agent_id,
                                                   req->required_knowledge_mask)) {
                refusal = DOM_PLAYER_REFUSAL_NO_KNOWLEDGE;
                ok = 0;
            } else if (!dom_player_check_physical(ctx, req)) {
                refusal = DOM_PLAYER_REFUSAL_PHYSICAL_CONSTRAINT;
                ok = 0;
            }
            break;
        }
        default:
            refusal = DOM_PLAYER_REFUSAL_INVALID_INTENT;
            ok = 0;
            break;
    }

    mutable_intent.status = ok ? DOM_PLAYER_INTENT_ACCEPTED : DOM_PLAYER_INTENT_REFUSED;
    mutable_intent.refusal = refusal;
    if (dom_player_enqueue(queue, &mutable_intent) != 0) {
        return -2;
    }
    if (ctx && ctx->events) {
        dom_player_event_record(ctx->events,
                                mutable_intent.player_id,
                                mutable_intent.agent_id,
                                ok ? DOM_PLAYER_EVENT_INTENT_ACCEPTED : DOM_PLAYER_EVENT_INTENT_REFUSED,
                                mutable_intent.intent_id,
                                refusal,
                                ctx->now_act);
    }
    return ok ? 0 : 1;
}
