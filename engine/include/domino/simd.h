/*
FILE: include/domino/simd.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / simd
RESPONSIBILITY: Defines the public contract for `simd` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
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

/* dsimd_result: Public type used by `simd`. */
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

/* dsimd_api_v1: Public type used by `simd`. */
typedef struct dsimd_api_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;

    /* Representative math kernels; semantics defined in a later spec. */
    void  (*vec4_add_f32)(float* out4, const float* a4, const float* b4);
    float (*dot3_f32)(const float* a3, const float* b3);
    void  (*mat4_mul_f32)(float* out16, const float* a16, const float* b16);
} dsimd_api_v1;

/* Purpose: Api dsimd get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dsimd_result dsimd_get_api(u32 requested_abi, dsimd_api_v1* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SIMD_H */

