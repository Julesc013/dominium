/*
FILE: engine/modules/execution/kernels/gpu/gpu_caps.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/gpu
RESPONSIBILITY: GPU compute capability detection (derived-only backend).
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Detection only; does not affect simulation truth.
*/
#ifndef DOMINO_EXECUTION_GPU_CAPS_H
#define DOMINO_EXECUTION_GPU_CAPS_H

#include "domino/core/types.h"
#include "domino/execution/kernel_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_GPU_CAP_COMPUTE = 1u << 0
};

typedef struct dom_gpu_caps {
    u32 cap_mask;
    u64 max_buffer_bytes;
} dom_gpu_caps;

void dom_gpu_detect_caps(dom_gpu_caps* out_caps);
void dom_gpu_set_caps_override(const dom_gpu_caps* caps);
void dom_gpu_clear_caps_override(void);
d_bool dom_gpu_caps_has(const dom_gpu_caps* caps, u32 required_mask);
u32 dom_gpu_backend_mask_from_caps(const dom_gpu_caps* caps);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_GPU_CAPS_H */
