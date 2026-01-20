/*
FILE: engine/modules/execution/kernels/scalar/scalar_kernels.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/scalar
RESPONSIBILITY: Scalar kernel implementations and registration.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Scalar implementations are deterministic by default.
*/
#ifndef DOMINO_EXECUTION_SCALAR_KERNELS_H
#define DOMINO_EXECUTION_SCALAR_KERNELS_H

#include "domino/core/types.h"
#include "domino/execution/kernel_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_kernel_fill_params {
    u32 element_size;
    unsigned char value[8];
} dom_kernel_fill_params;

typedef struct dom_kernel_apply_delta_params {
    const unsigned char* delta_bytes;
    u32 delta_size;
} dom_kernel_apply_delta_params;

typedef struct dom_kernel_visibility_params {
    u32 entity_count;
} dom_kernel_visibility_params;

#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus

#include "execution/kernels/kernel_registry.h"

void dom_register_scalar_kernels(dom_kernel_registry* registry);

#endif /* __cplusplus */

#endif /* DOMINO_EXECUTION_SCALAR_KERNELS_H */
