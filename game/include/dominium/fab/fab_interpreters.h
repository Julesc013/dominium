/*
FILE: include/dominium/fab/fab_interpreters.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / fab
RESPONSIBILITY: Minimal fabrication (FAB) interpreters for data-driven materials, interfaces, assemblies, and processes.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: All FAB evaluation is deterministic for identical inputs.
*/
#ifndef DOMINIUM_FAB_INTERPRETERS_H
#define DOMINIUM_FAB_INTERPRETERS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/rng.h"
#include "domino/fab.h"
#include "domino/process.h"
#include "dominium/physical/parts_and_assemblies.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Common types
 *------------------------------------------------------------*/

typedef enum dom_fab_overflow_behavior {
    DOM_FAB_OVERFLOW_REFUSE = 1
} dom_fab_overflow_behavior;

typedef enum dom_fab_aggregation_kind {
    DOM_FAB_AGG_SUM = 1,
    DOM_FAB_AGG_MIN = 2,
    DOM_FAB_AGG_MAX = 3,
    DOM_FAB_AGG_AVG = 4
} dom_fab_aggregation_kind;

typedef enum dom_fab_interp_kind {
    DOM_FAB_INTERP_STEP = 1,
    DOM_FAB_INTERP_LINEAR = 2
} dom_fab_interp_kind;

typedef struct dom_fab_unit_annotation {
    const char* key;
    const char* unit_id;
    u32         scale;
    u32         overflow_behavior;
} dom_fab_unit_annotation;

typedef struct dom_fab_quantity {
    q48_16      value_q48;
    const char* unit_id;
    u32         scale;
    u32         overflow_behavior;
} dom_fab_quantity;

/*------------------------------------------------------------
 * Material traits
 *------------------------------------------------------------*/

typedef struct dom_fab_trait {
    const char* trait_id;
    q48_16      value_q48;
    const char* unit_id;
    u32         aggregation;
    u32         interpolation;
} dom_fab_trait;

typedef struct dom_fab_material {
    const char* material_id;
    dom_fab_trait* traits;
    u32            trait_count;
    dom_fab_unit_annotation* unit_annotations;
    u32            unit_annotation_count;
} dom_fab_material;

typedef struct dom_fab_material_registry {
    dom_fab_material* materials;
    u32 count;
    u32 capacity;
} dom_fab_material_registry;

void dom_fab_material_registry_init(dom_fab_material_registry* reg,
                                    dom_fab_material* storage,
                                    u32 capacity);
int dom_fab_material_register(dom_fab_material_registry* reg,
                              const dom_fab_material* material);
const dom_fab_material* dom_fab_material_find(const dom_fab_material_registry* reg,
                                              const char* material_id);
const dom_fab_trait* dom_fab_material_trait_find(const dom_fab_material* material,
                                                 const char* trait_id);
int dom_fab_material_trait_interpolate(const dom_fab_material* a,
                                       const dom_fab_material* b,
                                       const char* trait_id,
                                       q16_16 t_q16,
                                       dom_fab_trait* out_trait);

/*------------------------------------------------------------
 * Interfaces and compatibility
 *------------------------------------------------------------*/

typedef struct dom_fab_interface_desc {
    const char* interface_id;
    const char* interface_type;
    const char* directionality;
    dom_fab_quantity capacity;
    u32 allow_degraded;
    dom_fab_unit_annotation* unit_annotations;
    u32 unit_annotation_count;
} dom_fab_interface_desc;

typedef struct dom_fab_interface_registry {
    dom_fab_interface_desc* interfaces;
    u32 count;
    u32 capacity;
} dom_fab_interface_registry;

void dom_fab_interface_registry_init(dom_fab_interface_registry* reg,
                                     dom_fab_interface_desc* storage,
                                     u32 capacity);
int dom_fab_interface_register(dom_fab_interface_registry* reg,
                               const dom_fab_interface_desc* desc);
const dom_fab_interface_desc* dom_fab_interface_find(const dom_fab_interface_registry* reg,
                                                     const char* interface_id);

typedef struct dom_fab_interface_compat_result {
    u32 compat;
    u32 refusal_code;
} dom_fab_interface_compat_result;

int dom_fab_interface_check_compat(const dom_fab_interface_desc* a,
                                   const dom_fab_interface_desc* b,
                                   dom_fab_interface_compat_result* out_result);

/*------------------------------------------------------------
 * Parts
 *------------------------------------------------------------*/

typedef struct dom_fab_part_desc {
    const char* part_id;
    const char* material_id;
    dom_fab_quantity mass;
    dom_fab_quantity volume;
    const char** interface_ids;
    u32 interface_count;
    const char** constraint_ids;
    u32 constraint_count;
    const char* quality_id;
    const char* failure_model_id;
    dom_fab_unit_annotation* unit_annotations;
    u32 unit_annotation_count;
} dom_fab_part_desc;

typedef struct dom_fab_part_registry {
    dom_fab_part_desc* parts;
    u32 count;
    u32 capacity;
} dom_fab_part_registry;

void dom_fab_part_registry_init(dom_fab_part_registry* reg,
                                dom_fab_part_desc* storage,
                                u32 capacity);
int dom_fab_part_register(dom_fab_part_registry* reg,
                          const dom_fab_part_desc* part);
const dom_fab_part_desc* dom_fab_part_find(const dom_fab_part_registry* reg,
                                           const char* part_id);

/*------------------------------------------------------------
 * Assemblies
 *------------------------------------------------------------*/

typedef enum dom_fab_node_type {
    DOM_FAB_NODE_PART = 1,
    DOM_FAB_NODE_SUBASSEMBLY = 2
} dom_fab_node_type;

typedef struct dom_fab_assembly_node {
    const char* node_id;
    u32 node_type;
    const char* ref_id;
} dom_fab_assembly_node;

typedef struct dom_fab_assembly_edge {
    const char* edge_id;
    const char* from_node_id;
    const char* to_node_id;
    const char* interface_id;
} dom_fab_assembly_edge;

typedef struct dom_fab_assembly_subsystem {
    const char* subsystem_id;
    const char** node_ids;
    u32 node_id_count;
} dom_fab_assembly_subsystem;

typedef struct dom_fab_metric {
    const char* metric_id;
    dom_fab_quantity value;
    u32 aggregation;
} dom_fab_metric;

enum {
    DOM_FAB_ASSEMBLY_ALLOW_CYCLES = 1u << 0
};

typedef struct dom_fab_assembly_desc {
    const char* assembly_id;
    dom_fab_assembly_node* nodes;
    u32 node_count;
    dom_fab_assembly_edge* edges;
    u32 edge_count;
    dom_fab_assembly_subsystem* subsystems;
    u32 subsystem_count;
    const char** hosted_process_ids;
    u32 hosted_process_count;
    dom_fab_metric* throughput_limits;
    u32 throughput_count;
    dom_fab_metric* maintenance;
    u32 maintenance_count;
    dom_fab_unit_annotation* unit_annotations;
    u32 unit_annotation_count;
    u32 flags;
} dom_fab_assembly_desc;

typedef struct dom_fab_assembly_registry {
    dom_fab_assembly_desc* assemblies;
    u32 count;
    u32 capacity;
} dom_fab_assembly_registry;

void dom_fab_assembly_registry_init(dom_fab_assembly_registry* reg,
                                    dom_fab_assembly_desc* storage,
                                    u32 capacity);
int dom_fab_assembly_register(dom_fab_assembly_registry* reg,
                              const dom_fab_assembly_desc* assembly);
const dom_fab_assembly_desc* dom_fab_assembly_find(const dom_fab_assembly_registry* reg,
                                                   const char* assembly_id);

typedef struct dom_fab_capacity_totals {
    q48_16 mechanical_q48;
    q48_16 electrical_q48;
    q48_16 fluid_q48;
    q48_16 data_q48;
    q48_16 thermal_q48;
} dom_fab_capacity_totals;

typedef struct dom_fab_assembly_aggregate {
    q48_16 total_mass_q48;
    q48_16 total_volume_q48;
    dom_fab_capacity_totals capacities;
    const char** hosted_process_ids;
    u32 hosted_process_count;
    u32 hosted_process_capacity;
    dom_fab_metric* throughput_limits;
    u32 throughput_count;
    u32 throughput_capacity;
    dom_fab_metric* maintenance;
    u32 maintenance_count;
    u32 maintenance_capacity;
} dom_fab_assembly_aggregate;

int dom_fab_assembly_validate(const dom_fab_assembly_desc* assembly,
                              const dom_fab_part_registry* parts,
                              const dom_fab_interface_registry* interfaces,
                              const dom_fab_assembly_registry* assemblies,
                              u32* out_refusal_code);

int dom_fab_assembly_aggregate_compute(const dom_fab_assembly_desc* assembly,
                                       const dom_fab_part_registry* parts,
                                       const dom_fab_interface_registry* interfaces,
                                       const dom_fab_assembly_registry* assemblies,
                                       dom_fab_assembly_aggregate* out_agg,
                                       u32* out_refusal_code);

/*------------------------------------------------------------
 * Process families and execution adapter
 *------------------------------------------------------------*/

typedef enum dom_fab_process_io_kind {
    DOM_FAB_PROCESS_IO_INPUT = 0,
    DOM_FAB_PROCESS_IO_OUTPUT = 1,
    DOM_FAB_PROCESS_IO_WASTE = 2
} dom_fab_process_io_kind;

typedef struct dom_fab_process_io {
    u32 io_id;
    const char* resource_id;
    dom_fab_quantity quantity;
    u32 kind;
} dom_fab_process_io;

typedef struct dom_fab_param_range {
    const char* param_id;
    q48_16 min_q48;
    q48_16 max_q48;
    const char* unit_id;
} dom_fab_param_range;

typedef struct dom_fab_param_value {
    const char* param_id;
    q48_16 value_q48;
    const char* unit_id;
} dom_fab_param_value;

typedef struct dom_fab_weighted_outcome {
    u32 outcome_id;
    u32 weight;
} dom_fab_weighted_outcome;

typedef struct dom_fab_constraint dom_fab_constraint;

typedef struct dom_fab_process_family {
    const char* process_family_id;
    dom_fab_process_io* inputs;
    u32 input_count;
    dom_fab_process_io* outputs;
    u32 output_count;
    dom_fab_process_io* waste;
    u32 waste_count;
    dom_fab_param_range* parameter_space;
    u32 parameter_count;
    dom_fab_weighted_outcome* yield_distribution;
    u32 yield_count;
    const dom_fab_constraint* constraints;
    u32 constraint_count;
    const char** required_instruments;
    u32 instrument_count;
    const char** required_standards;
    u32 standard_count;
    const u32* failure_mode_ids;
    u32 failure_mode_count;
    dom_fab_unit_annotation* unit_annotations;
    u32 unit_annotation_count;
} dom_fab_process_family;

typedef struct dom_fab_process_registry {
    dom_fab_process_family* families;
    u32 count;
    u32 capacity;
} dom_fab_process_registry;

void dom_fab_process_registry_init(dom_fab_process_registry* reg,
                                   dom_fab_process_family* storage,
                                   u32 capacity);
int dom_fab_process_register(dom_fab_process_registry* reg,
                             const dom_fab_process_family* family);
const dom_fab_process_family* dom_fab_process_find(const dom_fab_process_registry* reg,
                                                   const char* process_family_id);

typedef struct dom_fab_constraint {
    const char* constraint_id;
    const char* key;
    q48_16 min_q48;
    q48_16 max_q48;
    const char* unit_id;
} dom_fab_constraint;

typedef struct dom_fab_constraint_context {
    const dom_fab_param_value* values;
    u32 value_count;
} dom_fab_constraint_context;

int dom_fab_constraints_eval(const dom_fab_constraint* constraints,
                             u32 constraint_count,
                             const dom_fab_constraint_context* ctx,
                             u32* out_refusal_code);

typedef struct dom_fab_process_context {
    const dom_fab_param_value* parameters;
    u32 parameter_count;
    const char** instrument_ids;
    u32 instrument_count;
    const char** standard_ids;
    u32 standard_count;
    const dom_fab_constraint* constraints;
    u32 constraint_count;
    u32 rng_seed;
    const char* domain_id;
    const char* entity_id;
    const char* stream_id;
} dom_fab_process_context;

typedef struct dom_fab_process_result {
    int ok;
    u32 refusal_code;
    u32 failure_mode_id;
    u32 outcome_id;
    u32 cost_units;
} dom_fab_process_result;

int dom_fab_process_execute(const dom_fab_process_family* family,
                            const dom_fab_process_context* ctx,
                            dom_fab_process_result* out_result);

u32 dom_fab_seed_compose(u32 base_seed,
                         const char* domain_id,
                         const char* entity_id,
                         const char* stream_id);

u32 dom_fab_sample_bounded_u32(u32 seed,
                               u32 min_value,
                               u32 max_value);

int dom_fab_select_outcomes(const dom_fab_weighted_outcome* outcomes,
                            u32 outcome_count,
                            u32 seed,
                            u32 max_outcomes,
                            u32* out_ids,
                            u32* out_count);

int dom_fab_process_family_to_desc(const dom_fab_process_family* family,
                                   dom_process_desc* out_desc,
                                   dom_process_io_desc* io_storage,
                                   u32 io_storage_cap);

/*------------------------------------------------------------
 * Quality and failure hooks
 *------------------------------------------------------------*/

typedef struct dom_fab_quality_rule {
    const char* metric_id;
    q48_16 min_q48;
    q48_16 max_q48;
    const char* unit_id;
} dom_fab_quality_rule;

typedef struct dom_fab_quality_desc {
    const char* quality_id;
    dom_fab_quality_rule* rules;
    u32 rule_count;
} dom_fab_quality_desc;

typedef struct dom_fab_quality_measurement {
    const char* metric_id;
    q48_16 value_q48;
    const char* unit_id;
} dom_fab_quality_measurement;

int dom_fab_quality_evaluate(const dom_fab_quality_desc* quality,
                             const dom_fab_quality_measurement* measurements,
                             u32 measurement_count,
                             u32* out_refusal_code);

typedef enum dom_fab_failure_mode {
    DOM_FAB_FAILURE_ADD = 1,
    DOM_FAB_FAILURE_MULTIPLY = 2
} dom_fab_failure_mode;

typedef struct dom_fab_failure_rule {
    const char* trait_id;
    u32 mode;
    q48_16 value_q48;
    const char* unit_id;
} dom_fab_failure_rule;

typedef struct dom_fab_failure_model {
    const char* failure_model_id;
    dom_fab_failure_rule* rules;
    u32 rule_count;
} dom_fab_failure_model;

int dom_fab_failure_apply(const dom_fab_failure_model* model,
                          dom_fab_material* material,
                          u32* out_refusal_code);

/*------------------------------------------------------------
 * Placement and volume claims
 *------------------------------------------------------------*/

typedef struct dom_fab_volume_claim_desc {
    u64 claim_id;
    u64 owner_id;
    i32 min_x;
    i32 min_y;
    i32 max_x;
    i32 max_y;
} dom_fab_volume_claim_desc;

int dom_fab_volume_claim_register(dom_volume_claim_registry* reg,
                                  const dom_fab_volume_claim_desc* claim,
                                  dom_physical_audit_log* audit,
                                  dom_act_time_t now_act,
                                  u32* out_refusal_code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_FAB_INTERPRETERS_H */
