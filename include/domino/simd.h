#ifndef DOMINO_SIMD_H
#define DOMINO_SIMD_H
/*
 * Domino SIMD / math kernel facade template (C89/C++98 visible).
 *
 * This is an optional acceleration surface. Correctness must never depend on
 * its availability; a scalar baseline backend will be provided later.
 */

#include "domino/abi.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsimd_result_e {
    DSIMD_OK = 0,
    DSIMD_ERR,
    DSIMD_ERR_UNSUPPORTED
} dsimd_result;

/* Interface IDs (u32 constants) */
#define DSIMD_IID_API_V1 ((dom_iid)0x44534D01u)

/* Reserved extension slots (placeholders) */
#define DSIMD_IID_EXT_RESERVED0 ((dom_iid)0x44534D80u)
#define DSIMD_IID_EXT_RESERVED1 ((dom_iid)0x44534D81u)

typedef struct dsimd_api_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;

    /* Representative math kernels; semantics defined in a later spec. */
    void  (*vec4_add_f32)(float* out4, const float* a4, const float* b4);
    float (*dot3_f32)(const float* a3, const float* b3);
    void  (*mat4_mul_f32)(float* out16, const float* a16, const float* b16);
} dsimd_api_v1;

dsimd_result dsimd_get_api(u32 requested_abi, dsimd_api_v1* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SIMD_H */

