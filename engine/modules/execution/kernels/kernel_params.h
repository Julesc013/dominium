/*
FILE: engine/modules/execution/kernels/kernel_params.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Defines kernel dispatch requirement parameters.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Policy inputs only.
*/
#ifndef DOMINO_EXECUTION_KERNEL_PARAMS_H
#define DOMINO_EXECUTION_KERNEL_PARAMS_H

#include "domino/execution/kernel_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_kernel_requirements {
    u32 backend_mask;
    u32 required_capabilities;
    u32 flags;
} dom_kernel_requirements;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_KERNEL_PARAMS_H */
