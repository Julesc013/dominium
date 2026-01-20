/*
FILE: engine/modules/execution/kernels/kernel_selector.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Deterministic kernel backend selection utilities.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Selection for authoritative tasks must be deterministic.
*/
#ifndef DOMINO_EXECUTION_KERNEL_SELECTOR_H
#define DOMINO_EXECUTION_KERNEL_SELECTOR_H

#include "execution/kernels/kernel_policy.h"
#include "execution/kernels/kernel_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_KERNEL_PROFILE_NONE = 0u,
    DOM_KERNEL_PROFILE_SLOW = 1u << 0
};

typedef enum dom_kernel_select_status {
    DOM_KERNEL_SELECT_OK = 0,
    DOM_KERNEL_SELECT_NO_CANDIDATE = 1,
    DOM_KERNEL_SELECT_INVALID = 2
} dom_kernel_select_status;

typedef enum dom_kernel_select_reason {
    DOM_KERNEL_SELECT_REASON_NONE = 0,
    DOM_KERNEL_SELECT_REASON_NO_MATCH = 1
} dom_kernel_select_reason;

typedef struct dom_kernel_select_request {
    dom_kernel_op_id op_id;
    u32 determinism_class;
    u32 available_backend_mask;
    u32 law_backend_mask;
    u32 profile_flags;
    u32 derived_cpu_time_us;
} dom_kernel_select_request;

typedef struct dom_kernel_select_result {
    u32 status;
    u32 backend_id;
    u32 reason;
} dom_kernel_select_result;

int dom_kernel_select_backend(const dom_kernel_policy* policy,
                              const dom_kernel_select_request* req,
                              dom_kernel_select_result* out_result);
const dom_kernel_entry* dom_kernel_select_entry(const dom_kernel_registry* registry,
                                                const dom_kernel_policy* policy,
                                                const dom_kernel_select_request* req,
                                                dom_kernel_select_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_KERNEL_SELECTOR_H */
