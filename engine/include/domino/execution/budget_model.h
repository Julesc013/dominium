/*
FILE: include/domino/execution/budget_model.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/budget_model
RESPONSIBILITY: Defines deterministic budget profile inputs and outputs.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: No wall-clock inputs; deterministic scaling only.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned via schema docs.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_BUDGET_MODEL_H
#define DOMINO_EXECUTION_BUDGET_MODEL_H

#include "domino/core/types.h"
#include "domino/sys/sys_caps.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_EXEC_BUDGET_ID_MAX 32u
#define DOM_EXEC_DEGRADATION_ID_MAX 32u

typedef enum dom_exec_memory_budget_class {
    DOM_EXEC_MEM_UNKNOWN = 0,
    DOM_EXEC_MEM_SMALL = 1,
    DOM_EXEC_MEM_MEDIUM = 2,
    DOM_EXEC_MEM_LARGE = 3,
    DOM_EXEC_MEM_HUGE = 4
} dom_exec_memory_budget_class;

typedef struct dom_exec_budget_profile {
    char budget_profile_id[DOM_EXEC_BUDGET_ID_MAX];
    u32 base_cpu_authoritative;
    u32 base_cpu_derived;
    u32 base_io_derived;
    u32 base_net;
    u32 memory_class; /* dom_exec_memory_budget_class */
    char degradation_policy_id[DOM_EXEC_DEGRADATION_ID_MAX];
    u32 cpu_scale_min;
    u32 cpu_scale_max;
    u32 io_scale_max;
    u32 net_scale_max;
} dom_exec_budget_profile;

typedef struct dom_exec_budget_result {
    u32 per_tick_cpu_budget_units_authoritative;
    u32 per_tick_cpu_budget_units_derived;
    u32 per_tick_io_budget_units_derived;
    u32 per_tick_net_budget_units;
    u32 memory_class; /* dom_exec_memory_budget_class */
    u32 cpu_scale;
    u32 io_scale;
    u32 net_scale;
    char degradation_policy_id[DOM_EXEC_DEGRADATION_ID_MAX];
} dom_exec_budget_result;

void dom_exec_budget_profile_init(dom_exec_budget_profile* profile);
int dom_exec_budget_resolve(const dom_sys_caps_v1* caps,
                            const dom_exec_budget_profile* profile,
                            dom_exec_budget_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_BUDGET_MODEL_H */
