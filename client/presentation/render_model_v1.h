/*
FILE: client/presentation/render_model_v1.h
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: RenderModel contract derived from PerceivedModel only.
ALLOWED DEPENDENCIES: perceived_model_v1.h and domino/core/types.h.
FORBIDDEN DEPENDENCIES: domino/truth_model_v1.h and authoritative simulation mutation APIs.
DETERMINISM: RenderModel derivation ordering is deterministic for identical PerceivedModel input.
*/
#ifndef DOMINIUM_CLIENT_PRESENTATION_RENDER_MODEL_V1_H
#define DOMINIUM_CLIENT_PRESENTATION_RENDER_MODEL_V1_H

#include "domino/core/types.h"
#include "perceived_model_v1.h"

typedef struct dom_renderable_v1 {
    const char* renderable_id;
    const char* entity_id;
    const char* transform_ref;
} dom_renderable_v1;

typedef struct dom_render_model_v1 {
    const char* schema_version;
    const char* source_perceived_hash;
    const char* viewpoint_id;
    const char* lens_id;
    const dom_renderable_v1* renderables;
    u32 renderable_count;
} dom_render_model_v1;

int dom_build_render_model_v1(const dom_perceived_model_v1* perceived,
                              const char* perceived_hash,
                              dom_render_model_v1* out_model);

#endif /* DOMINIUM_CLIENT_PRESENTATION_RENDER_MODEL_V1_H */
