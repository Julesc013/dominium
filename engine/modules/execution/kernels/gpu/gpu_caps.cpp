/*
FILE: engine/modules/execution/kernels/gpu/gpu_caps.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/gpu
RESPONSIBILITY: GPU compute capability detection (derived-only backend).
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Detection only; does not affect simulation truth.
*/
#include "execution/kernels/gpu/gpu_caps.h"

static d_bool g_gpu_caps_override_enabled = D_FALSE;
static dom_gpu_caps g_gpu_caps_override = { 0u, 0u };

void dom_gpu_detect_caps(dom_gpu_caps* out_caps)
{
    if (!out_caps) {
        return;
    }
    if (g_gpu_caps_override_enabled) {
        *out_caps = g_gpu_caps_override;
        return;
    }
    out_caps->cap_mask = 0u;
    out_caps->max_buffer_bytes = 0u;
}

void dom_gpu_set_caps_override(const dom_gpu_caps* caps)
{
    if (!caps) {
        return;
    }
    g_gpu_caps_override = *caps;
    g_gpu_caps_override_enabled = D_TRUE;
}

void dom_gpu_clear_caps_override(void)
{
    g_gpu_caps_override_enabled = D_FALSE;
}

d_bool dom_gpu_caps_has(const dom_gpu_caps* caps, u32 required_mask)
{
    if (!caps) {
        return D_FALSE;
    }
    if (required_mask == 0u) {
        return D_TRUE;
    }
    return ((caps->cap_mask & required_mask) == required_mask) ? D_TRUE : D_FALSE;
}

u32 dom_gpu_backend_mask_from_caps(const dom_gpu_caps* caps)
{
    u32 mask = DOM_KERNEL_BACKEND_MASK_SCALAR;
    if (caps && (caps->cap_mask & DOM_GPU_CAP_COMPUTE)) {
        mask |= DOM_KERNEL_BACKEND_MASK_GPU;
    }
    return mask;
}
