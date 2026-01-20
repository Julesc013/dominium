/*
FILE: engine/modules/execution/kernels/gpu/gpu_kernels.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/gpu
RESPONSIBILITY: GPU kernel backend for derived tasks.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: GPU results are derived-only; authoritative tasks must not select this backend.
*/
#ifndef DOMINO_EXECUTION_GPU_KERNELS_H
#define DOMINO_EXECUTION_GPU_KERNELS_H

#include "execution/kernels/gpu/gpu_caps.h"

#ifdef __cplusplus

#include "execution/kernels/kernel_registry.h"

void dom_register_gpu_kernels(dom_kernel_registry* registry,
                              const dom_gpu_caps* caps);

u32 dom_gpu_kernels_pending(void);
void dom_gpu_kernels_process(u32 max_jobs);
void dom_gpu_kernels_clear(void);

#endif /* __cplusplus */

#endif /* DOMINO_EXECUTION_GPU_KERNELS_H */
