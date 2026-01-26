/*
FILE: include/dominium/physical/local_processes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines local physical interaction processes (survey, collect, assemble, connect, inspect, repair).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Local process outcomes are deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_LOCAL_PROCESSES_H
#define DOMINIUM_PHYSICAL_LOCAL_PROCESSES_H

#include "dominium/physical/field_storage.h"
#include "dominium/physical/parts_and_assemblies.h"
#include "dominium/physical/network_graph.h"
#include "dominium/physical/physical_process.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_local_process_kind {
    DOM_LOCAL_PROCESS_SURVEY = 1,
    DOM_LOCAL_PROCESS_COLLECT = 2,
    DOM_LOCAL_PROCESS_ASSEMBLE = 3,
    DOM_LOCAL_PROCESS_CONNECT_ENERGY = 4,
    DOM_LOCAL_PROCESS_INSPECT = 5,
    DOM_LOCAL_PROCESS_REPAIR = 6
} dom_local_process_kind;

typedef struct dom_local_process_desc {
    u32 kind;
    u32 required_field_mask;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 cost_units;
    i32 max_surface_gradient_q16;
    i32 min_support_capacity_q16;
    i32 resource_amount_q16;
    i32 energy_load_q16;
} dom_local_process_desc;

typedef struct dom_local_structure_state {
    u64 structure_id;
    u32 built;
    u32 failed;
} dom_local_structure_state;

typedef struct dom_local_process_world {
    dom_field_storage* objective_fields;
    dom_field_storage* subjective_fields;
    dom_assembly* assembly;
    dom_volume_claim_registry* claims;
    dom_network_graph* network;
    dom_local_structure_state* structure;
} dom_local_process_world;

typedef struct dom_local_process_context {
    dom_physical_process_context phys;
    u64 rng_seed;
    u32 knowledge_mask;
    u32 confidence_q16;
} dom_local_process_context;

typedef struct dom_local_process_result {
    dom_physical_process_result process;
    u32 surveyed_field_mask;
    u32 confidence_q16;
    u32 uncertainty_q16;
} dom_local_process_result;

void dom_local_process_desc_default(u32 kind,
                                    dom_local_process_desc* out_desc);

int dom_local_process_apply(dom_local_process_world* world,
                            const dom_local_process_desc* desc,
                            u32 x,
                            u32 y,
                            const dom_local_process_context* ctx,
                            dom_local_process_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_LOCAL_PROCESSES_H */
