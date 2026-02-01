/*
FILE: include/domino/jobs.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / jobs
RESPONSIBILITY: Defines the public contract for `jobs` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_JOBS_H
#define DOMINO_JOBS_H
/*
 * Domino jobs facade template (C89/C++98 visible).
 *
 * This header defines versioned, POD-only vtable templates for a future job
 * system backend. It is intentionally header-only (no implementation).
 */

#include "domino/abi.h"

#ifdef __cplusplus
extern "C" {
#endif

/* djobs_result: Public type used by `jobs`. */
typedef enum djobs_result_e {
    DJOBS_OK = 0,
    DJOBS_ERR,
    DJOBS_ERR_UNSUPPORTED
} djobs_result;

/* Interface IDs (u32 constants) */
#define DJOBS_IID_API_V1 ((dom_iid)0x444A4F01u)

/* Reserved extension slots (placeholders) */
#define DJOBS_IID_EXT_RESERVED0 ((dom_iid)0x444A4F80u)
#define DJOBS_IID_EXT_RESERVED1 ((dom_iid)0x444A4F81u)

/* djobs_context: Public type used by `jobs`. */
typedef struct djobs_context_s djobs_context;

/* user: Public type used by `jobs`. */
typedef void (*djobs_job_fn)(void* user);

/* djobs_desc_v1: Public type used by `jobs`. */
typedef struct djobs_desc_v1 {
    DOM_ABI_HEADER;
    u32 requested_worker_count;
    u32 flags;
} djobs_desc_v1;

/* djobs_job_desc_v1: Public type used by `jobs`. */
typedef struct djobs_job_desc_v1 {
    DOM_ABI_HEADER;
    djobs_job_fn fn;
    void* user;
} djobs_job_desc_v1;

/* djobs_api_v1: Public type used by `jobs`. */
typedef struct djobs_api_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;

    djobs_context* (*create)(const djobs_desc_v1* desc);
    void (*destroy)(djobs_context* ctx);

    djobs_result (*submit)(djobs_context* ctx,
                           const djobs_job_desc_v1* jobs,
                           u32 job_count);

    void (*wait_idle)(djobs_context* ctx);
} djobs_api_v1;

/* Purpose: Api djobs get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
djobs_result djobs_get_api(u32 requested_abi, djobs_api_v1* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_JOBS_H */

