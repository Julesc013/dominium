/*
FILE: client/observability/perceived_model_v1.c
MODULE: Dominium
LAYER / SUBSYSTEM: Client / observation
RESPONSIBILITY: Minimal immutable PerceivedModel helpers.
ALLOWED DEPENDENCIES: perceived_model_v1.h.
FORBIDDEN DEPENDENCIES: TruthModel headers and mutation APIs.
DETERMINISM: Helper accessors are pure and deterministic.
*/
#include "perceived_model_v1.h"

u32 dom_perceived_model_entity_count_v1(const dom_perceived_model_v1* model)
{
    if (!model) {
        return 0u;
    }
    return model->observed_entity_count;
}

u32 dom_perceived_model_field_count_v1(const dom_perceived_model_v1* model)
{
    if (!model) {
        return 0u;
    }
    return model->observed_field_count;
}
