/*
FILE: engine/modules/execution/kernels/simd/simd_kernels.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/simd
RESPONSIBILITY: SIMD kernel implementations and registration.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: SIMD variants must match scalar outputs for authoritative tasks.
*/
#ifndef DOMINO_EXECUTION_SIMD_KERNELS_H
#define DOMINO_EXECUTION_SIMD_KERNELS_H

#include "execution/kernels/simd/simd_caps.h"

#ifdef __cplusplus

#include "execution/kernels/kernel_registry.h"

void dom_register_simd_kernels(dom_kernel_registry* registry,
                               const dom_simd_caps* caps);

#endif /* __cplusplus */

#endif /* DOMINO_EXECUTION_SIMD_KERNELS_H */
