#ifndef DSK_RESUME_H
#define DSK_RESUME_H

#include "dsk_error.h"
#include "dsk_types.h"

#if defined(__cplusplus)
struct dss_services_t;
#else
struct dss_services_t;
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsk_apply_request_t {
    const struct dss_services_t *services;
    const dsk_u8 *plan_bytes;
    dsk_u32 plan_size;
    const char *out_state_path;
    const char *out_audit_path;
    const char *out_journal_path;
    dsk_u8 dry_run;
} dsk_apply_request_t;

DSK_API void dsk_apply_request_init(dsk_apply_request_t *req);
DSK_API dsk_status_t dsk_apply_plan(const dsk_apply_request_t *req);

typedef struct dsk_resume_request_t {
    const struct dss_services_t *services;
    const char *journal_path;
    const char *out_state_path;
    const char *out_audit_path;
} dsk_resume_request_t;

DSK_API void dsk_resume_request_init(dsk_resume_request_t *req);
DSK_API dsk_status_t dsk_resume(const dsk_resume_request_t *req);
DSK_API dsk_status_t dsk_rollback(const dsk_resume_request_t *req);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_RESUME_H */
