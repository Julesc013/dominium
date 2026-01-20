/*
FILE: engine/modules/execution/kernels/simd/simd_caps.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/simd
RESPONSIBILITY: Runtime SIMD capability detection.
ALLOWED DEPENDENCIES: engine/include public headers, C++98 headers, and platform headers as needed.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Detection only; does not affect simulation truth.
*/
#ifndef DOMINO_EXECUTION_SIMD_CAPS_H
#define DOMINO_EXECUTION_SIMD_CAPS_H

#include "domino/core/types.h"
#include "domino/execution/kernel_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_SIMD_CAP_SSE2   = 1u << 0,
    DOM_SIMD_CAP_SSE41  = 1u << 1,
    DOM_SIMD_CAP_AVX2   = 1u << 2,
    DOM_SIMD_CAP_AVX512 = 1u << 3,
    DOM_SIMD_CAP_NEON   = 1u << 4
};

#define DOM_SIMD_CAP_ANY (DOM_SIMD_CAP_SSE2 | DOM_SIMD_CAP_SSE41 | \
                          DOM_SIMD_CAP_AVX2 | DOM_SIMD_CAP_AVX512 | \
                          DOM_SIMD_CAP_NEON)

typedef struct dom_simd_caps {
    u32 mask;
} dom_simd_caps;

void dom_simd_detect_caps(dom_simd_caps* out_caps);
d_bool dom_simd_caps_has(const dom_simd_caps* caps, u32 required_mask);
u32 dom_simd_backend_mask_from_caps(const dom_simd_caps* caps);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_SIMD_CAPS_H */
