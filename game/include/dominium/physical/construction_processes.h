/*
FILE: include/dominium/physical/construction_processes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines construction process steps over assemblies and volume claims.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Construction process outcomes are deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_CONSTRUCTION_PROCESSES_H
#define DOMINIUM_PHYSICAL_CONSTRUCTION_PROCESSES_H

#include "dominium/physical/field_storage.h"
#include "dominium/physical/parts_and_assemblies.h"
#include "dominium/physical/physical_process.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_construction_process_kind {
    DOM_CONSTRUCT_SURVEY_SITE = 1,
    DOM_CONSTRUCT_PREPARE_GROUND = 2,
    DOM_CONSTRUCT_LAY_FOUNDATION = 3,
    DOM_CONSTRUCT_PLACE_PART = 4,
    DOM_CONSTRUCT_CONNECT_INTERFACE = 5,
    DOM_CONSTRUCT_INSPECT = 6,
    DOM_CONSTRUCT_CERTIFY = 7
} dom_construction_process_kind;

typedef struct dom_construction_process_desc {
    u32 kind;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 cost_units;
} dom_construction_process_desc;

typedef struct dom_construction_request {
    u32 kind;
    u32 x;
    u32 y;
    const dom_physical_part_desc* part_desc;
    u32 part_a;
    u32 part_b;
    u32 interface_mask;
    u32 ground_part_index;
    const dom_volume_claim* claim;
} dom_construction_request;

void dom_construction_process_desc_default(u32 kind,
                                           dom_construction_process_desc* out_desc);

int dom_construction_apply(dom_assembly* assembly,
                           dom_field_storage* fields,
                           dom_volume_claim_registry* claims,
                           const dom_construction_process_desc* desc,
                           const dom_construction_request* request,
                           const dom_physical_process_context* ctx,
                           dom_physical_process_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_CONSTRUCTION_PROCESSES_H */
