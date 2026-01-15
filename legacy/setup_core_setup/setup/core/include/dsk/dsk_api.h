#ifndef DSK_API_H
#define DSK_API_H

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

typedef dsk_status_t (*dsk_byte_sink_write_fn)(void *user,
                                               const dsk_u8 *data,
                                               dsk_u32 len);

typedef struct dsk_byte_sink_t {
    void *user;
    dsk_byte_sink_write_fn write;
} dsk_byte_sink_t;

typedef struct dsk_kernel_request_t {
    const struct dss_services_t *services;
    const dsk_u8 *manifest_bytes;
    dsk_u32 manifest_size;
    const dsk_u8 *request_bytes;
    dsk_u32 request_size;
    const dsk_u8 *installed_state_bytes;
    dsk_u32 installed_state_size;
    dsk_byte_sink_t out_plan;
    dsk_byte_sink_t out_state;
    dsk_byte_sink_t out_audit;
    /* deterministic_mode=1 forces run_id=0 and deterministic outputs. */
    dsk_u8 deterministic_mode;
} dsk_kernel_request_t;

DSK_API void dsk_kernel_request_init(dsk_kernel_request_t *req);

/* Extended request: adds optional structured log sink. */
typedef struct dsk_kernel_request_ex_t {
    dsk_kernel_request_t base;
    dsk_byte_sink_t out_log;
} dsk_kernel_request_ex_t;

DSK_API void dsk_kernel_request_ex_init(dsk_kernel_request_ex_t *req);

typedef struct dsk_import_request_t {
    const struct dss_services_t *services;
    const dsk_u8 *legacy_state_bytes;
    dsk_u32 legacy_state_size;
    dsk_byte_sink_t out_state;
    dsk_byte_sink_t out_audit;
    dsk_u8 deterministic_mode;
} dsk_import_request_t;

DSK_API void dsk_import_request_init(dsk_import_request_t *req);
DSK_API dsk_status_t dsk_import_legacy_state(const dsk_import_request_t *req);

DSK_API dsk_status_t dsk_install(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_upgrade(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_repair(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_uninstall(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_verify(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_status(const dsk_kernel_request_t *req);

DSK_API dsk_status_t dsk_install_ex(const dsk_kernel_request_ex_t *req);
DSK_API dsk_status_t dsk_upgrade_ex(const dsk_kernel_request_ex_t *req);
DSK_API dsk_status_t dsk_repair_ex(const dsk_kernel_request_ex_t *req);
DSK_API dsk_status_t dsk_uninstall_ex(const dsk_kernel_request_ex_t *req);
DSK_API dsk_status_t dsk_verify_ex(const dsk_kernel_request_ex_t *req);
DSK_API dsk_status_t dsk_status_ex(const dsk_kernel_request_ex_t *req);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_API_H */
