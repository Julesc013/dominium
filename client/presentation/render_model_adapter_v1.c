/*
FILE: client/presentation/render_model_adapter_v1.c
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: Minimal RenderModel adapter that consumes PerceivedModel only.
ALLOWED DEPENDENCIES: render_model_v1.h.
FORBIDDEN DEPENDENCIES: TruthModel headers and direct authoritative state access.
DETERMINISM: Adapter output is deterministic for identical PerceivedModel input.
*/
#include "render_model_v1.h"

int dom_build_render_model_v1(const dom_perceived_model_v1* perceived,
                              const char* perceived_hash,
                              dom_render_model_v1* out_model)
{
    if (!perceived || !out_model) {
        return -1;
    }

    out_model->schema_version = "1.0.0";
    out_model->source_perceived_hash = perceived_hash ? perceived_hash : "";
    out_model->viewpoint_id = perceived->viewpoint_id ? perceived->viewpoint_id : "";
    out_model->lens_id = perceived->lens_id ? perceived->lens_id : "";
    out_model->renderables = 0;
    out_model->renderable_count = perceived->observed_entity_count;
    return 0;
}
