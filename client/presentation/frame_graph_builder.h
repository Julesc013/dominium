/*
FILE: client/presentation/frame_graph_builder.h
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: Deterministic frame graph descriptor builder for render prep.
ALLOWED DEPENDENCIES: engine/include/**, game/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Frame graph IDs and pass counts are stable for identical inputs.
*/
#ifndef DOMINIUM_CLIENT_PRESENTATION_FRAME_GRAPH_BUILDER_H
#define DOMINIUM_CLIENT_PRESENTATION_FRAME_GRAPH_BUILDER_H

#include "domino/core/types.h"
#include "dominium/fidelity.h"

typedef struct dom_render_prep_inputs {
    u64 scene_id;
    u64 packed_view_set_id;
    u64 visibility_mask_set_id;
    u32 visible_region_count;
    u32 instance_count;
} dom_render_prep_inputs;

typedef struct dom_frame_graph_desc {
    u64 graph_id;
    u32 pass_count;
    u32 flags;
} dom_frame_graph_desc;

typedef struct dom_frame_graph_builder {
    u64 seed;
    dom_frame_graph_desc last_desc;
} dom_frame_graph_builder;

enum dom_frame_graph_flags {
    DOM_FRAME_GRAPH_REUSE = 1u << 0
};

void dom_frame_graph_builder_init(dom_frame_graph_builder* builder, u64 seed);
void dom_frame_graph_builder_build(dom_frame_graph_builder* builder,
                                   const dom_render_prep_inputs* inputs,
                                   dom_fidelity_tier tier,
                                   dom_frame_graph_desc* out_desc);

#endif /* DOMINIUM_CLIENT_PRESENTATION_FRAME_GRAPH_BUILDER_H */
