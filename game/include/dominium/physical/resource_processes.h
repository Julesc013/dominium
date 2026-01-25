/*
FILE: include/dominium/physical/resource_processes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines resource survey/extraction/refinement processes.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resource process outcomes are deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_RESOURCE_PROCESSES_H
#define DOMINIUM_PHYSICAL_RESOURCE_PROCESSES_H

#include "dominium/physical/field_storage.h"
#include "dominium/physical/physical_process.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_resource_process_kind {
    DOM_RESOURCE_SURVEY_DEPOSIT = 1,
    DOM_RESOURCE_ACCESS_DEPOSIT = 2,
    DOM_RESOURCE_EXTRACT_MATERIAL = 3,
    DOM_RESOURCE_REFINE_MATERIAL = 4,
    DOM_RESOURCE_HANDLE_TAILINGS = 5,
    DOM_RESOURCE_TRANSPORT_OUTPUT = 6
} dom_resource_process_kind;

typedef struct dom_resource_process_desc {
    u32 kind;
    u32 field_id;
    i32 amount_q16;
    i32 yield_q16;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 cost_units;
} dom_resource_process_desc;

typedef struct dom_resource_process_result {
    dom_physical_process_result process;
    i32 extracted_q16;
    i32 refined_q16;
    i32 waste_q16;
    i32 surveyed_q16;
} dom_resource_process_result;

void dom_resource_process_desc_default(u32 kind,
                                       dom_resource_process_desc* out_desc);

int dom_resource_apply_process(dom_field_storage* fields,
                               const dom_resource_process_desc* desc,
                               u32 x,
                               u32 y,
                               const dom_physical_process_context* ctx,
                               dom_resource_process_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_RESOURCE_PROCESSES_H */
