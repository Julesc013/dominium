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

typedef struct djobs_context_s djobs_context;

typedef void (*djobs_job_fn)(void* user);

typedef struct djobs_desc_v1 {
    DOM_ABI_HEADER;
    u32 requested_worker_count;
    u32 flags;
} djobs_desc_v1;

typedef struct djobs_job_desc_v1 {
    DOM_ABI_HEADER;
    djobs_job_fn fn;
    void* user;
} djobs_job_desc_v1;

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

djobs_result djobs_get_api(u32 requested_abi, djobs_api_v1* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_JOBS_H */

