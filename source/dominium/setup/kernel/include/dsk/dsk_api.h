#ifndef DSK_API_H
#define DSK_API_H

#include "dsk_error.h"
#include "dsk_types.h"

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
    const dsk_u8 *manifest_bytes;
    dsk_u32 manifest_size;
    const dsk_u8 *request_bytes;
    dsk_u32 request_size;
    dsk_byte_sink_t out_state;
    dsk_byte_sink_t out_audit;
    /* deterministic_mode=1 forces run_id=0 and deterministic outputs. */
    dsk_u8 deterministic_mode;
} dsk_kernel_request_t;

DSK_API void dsk_kernel_request_init(dsk_kernel_request_t *req);

DSK_API dsk_status_t dsk_install(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_repair(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_uninstall(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_verify(const dsk_kernel_request_t *req);
DSK_API dsk_status_t dsk_status(const dsk_kernel_request_t *req);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_API_H */
