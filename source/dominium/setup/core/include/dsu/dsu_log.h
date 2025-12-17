/*
FILE: source/dominium/setup/core/include/dsu/dsu_log.h
MODULE: Dominium Setup
PURPOSE: Audit log event emission and deterministic (de)serialization.
*/
#ifndef DSU_LOG_H_INCLUDED
#define DSU_LOG_H_INCLUDED

#include "dsu_ctx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_log dsu_log_t;

DSU_API dsu_status_t dsu_log_create(dsu_ctx_t *ctx, dsu_log_t **out_log);
DSU_API void dsu_log_destroy(dsu_ctx_t *ctx, dsu_log_t *log);
DSU_API dsu_status_t dsu_log_reset(dsu_ctx_t *ctx, dsu_log_t *log);

DSU_API dsu_status_t dsu_log_emit(dsu_ctx_t *ctx,
                                 dsu_log_t *log,
                                 dsu_u32 event_id,
                                 dsu_u8 severity,
                                 dsu_u8 category,
                                 const char *message);

DSU_API dsu_u32 dsu_log_event_count(const dsu_log_t *log);

DSU_API dsu_status_t dsu_log_event_get(const dsu_log_t *log,
                                      dsu_u32 index,
                                      dsu_u32 *out_event_id,
                                      dsu_u8 *out_severity,
                                      dsu_u8 *out_category,
                                      dsu_u32 *out_timestamp,
                                      const char **out_message);

DSU_API dsu_status_t dsu_log_write_file(dsu_ctx_t *ctx, const dsu_log_t *log, const char *path);
DSU_API dsu_status_t dsu_log_read_file(dsu_ctx_t *ctx, const char *path, dsu_log_t **out_log);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LOG_H_INCLUDED */

