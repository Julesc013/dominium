/*
FILE: client/observability/perceived_model_v1.h
MODULE: Dominium
LAYER / SUBSYSTEM: Client / observation
RESPONSIBILITY: Immutable PerceivedModel contract derived from TruthModel via Observation Kernel.
ALLOWED DEPENDENCIES: domino/core/types.h only.
FORBIDDEN DEPENDENCIES: authoritative mutation APIs.
DETERMINISM: Identical observation inputs produce identical PerceivedModel payloads.
*/
#ifndef DOMINIUM_CLIENT_OBSERVABILITY_PERCEIVED_MODEL_V1_H
#define DOMINIUM_CLIENT_OBSERVABILITY_PERCEIVED_MODEL_V1_H

#include "domino/core/types.h"

typedef struct dom_perceived_field_v1 {
    const char* field_id;
    const char* value;
} dom_perceived_field_v1;

typedef struct dom_perceived_model_v1 {
    const char* schema_version;
    const char* viewpoint_id;
    const char* lens_id;
    const char* epistemic_scope_id;
    const char* visibility_level;
    u64 simulation_tick;
    const char** observed_entities;
    u32 observed_entity_count;
    const dom_perceived_field_v1* observed_fields;
    u32 observed_field_count;
} dom_perceived_model_v1;

u32 dom_perceived_model_entity_count_v1(const dom_perceived_model_v1* model);
u32 dom_perceived_model_field_count_v1(const dom_perceived_model_v1* model);

#endif /* DOMINIUM_CLIENT_OBSERVABILITY_PERCEIVED_MODEL_V1_H */
