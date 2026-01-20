/*
FILE: client/presentation/frame_graph_builder.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: Deterministic frame graph descriptor builder.
ALLOWED DEPENDENCIES: engine/include/**, game/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Frame graph IDs and pass counts are stable for identical inputs.
*/
#include "frame_graph_builder.h"

static u64 dom_fg_hash_init(u64 seed)
{
    return seed ? seed : 1469598103934665603ULL;
}

static u64 dom_fg_hash_update_u32(u64 hash, u32 v)
{
    u32 i;
    for (i = 0u; i < 4u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u64 dom_fg_hash_update_u64(u64 hash, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_fg_passes_for_tier(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS: return 3u;
        case DOM_FIDELITY_MICRO: return 3u;
        case DOM_FIDELITY_MESO: return 2u;
        case DOM_FIDELITY_MACRO: return 1u;
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

void dom_frame_graph_builder_init(dom_frame_graph_builder* builder, u64 seed)
{
    if (!builder) {
        return;
    }
    builder->seed = seed;
    builder->last_desc.graph_id = seed;
    builder->last_desc.pass_count = 0u;
    builder->last_desc.flags = DOM_FRAME_GRAPH_REUSE;
}

void dom_frame_graph_builder_build(dom_frame_graph_builder* builder,
                                   const dom_render_prep_inputs* inputs,
                                   dom_fidelity_tier tier,
                                   dom_frame_graph_desc* out_desc)
{
    u64 hash;
    u32 pass_count;
    if (!builder || !out_desc) {
        return;
    }

    hash = dom_fg_hash_init(builder->seed);
    if (inputs) {
        hash = dom_fg_hash_update_u64(hash, inputs->scene_id);
        hash = dom_fg_hash_update_u64(hash, inputs->packed_view_set_id);
        hash = dom_fg_hash_update_u64(hash, inputs->visibility_mask_set_id);
        hash = dom_fg_hash_update_u32(hash, inputs->visible_region_count);
        hash = dom_fg_hash_update_u32(hash, inputs->instance_count);
    }
    hash = dom_fg_hash_update_u32(hash, (u32)tier);

    pass_count = dom_fg_passes_for_tier(tier);
    out_desc->graph_id = hash;
    out_desc->pass_count = pass_count;
    out_desc->flags = (tier == DOM_FIDELITY_LATENT) ? DOM_FRAME_GRAPH_REUSE : 0u;

    builder->last_desc = *out_desc;
}
