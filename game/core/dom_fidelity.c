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
                              u32 object_capacity)
{
    if (!ctx || !object_storage) {
        return -1;
    }
    ctx->objects = object_storage;
    ctx->object_capacity = object_capacity;
    ctx->object_count = 0u;
    memset(ctx->objects, 0, sizeof(dom_fidelity_object) * (size_t)object_capacity);
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
