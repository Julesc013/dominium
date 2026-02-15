/*
FILE: engine/include/domino/truth_model_v1.h
MODULE: Dominium
LAYER / SUBSYSTEM: Engine / authoritative truth contract
RESPONSIBILITY: Defines the minimal TruthModel contract for observation boundaries.
ALLOWED DEPENDENCIES: domino/core/types.h only.
FORBIDDEN DEPENDENCIES: renderer/presentation includes in boundary-guarded compilation units.
DETERMINISM: TruthModel references are deterministic input to observation derivation.
*/
#ifndef DOMINO_TRUTH_MODEL_V1_H
#define DOMINO_TRUTH_MODEL_V1_H

#if defined(DOMINIUM_RENDERER_BOUNDARY)
#error "Renderer boundary violation: renderer sources must not include domino/truth_model_v1.h"
#endif

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_truth_registry_refs_v1 {
    const char* domain_registry_hash;
    const char* law_registry_hash;
    const char* experience_registry_hash;
    const char* lens_registry_hash;
    const char* astronomy_catalog_index_hash;
    const char* ui_registry_hash;
} dom_truth_registry_refs_v1;

typedef struct dom_truth_model_v1 {
    const char* schema_version;
    const char* universe_identity_ref;
    const char* universe_state_ref;
    dom_truth_registry_refs_v1 registry_refs;
    u64 simulation_tick;
} dom_truth_model_v1;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_TRUTH_MODEL_V1_H */
