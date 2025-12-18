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

typedef enum dsu_log_phase_t {
    DSU_LOG_PHASE_STAGE = 0,
    DSU_LOG_PHASE_VERIFY = 1,
    DSU_LOG_PHASE_COMMIT = 2,
    DSU_LOG_PHASE_ROLLBACK = 3,
    DSU_LOG_PHASE_STATE = 4,
    DSU_LOG_PHASE_CLI = 5
} dsu_log_phase_t;

typedef struct dsu_log_event_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_u32 event_seq; /* 0 => assigned automatically */
    dsu_u32 event_id;

    dsu_u8 severity;
    dsu_u8 category;
    dsu_u8 phase;
    dsu_u8 reserved8;

    dsu_u32 timestamp; /* 0 in deterministic mode */

    /* Payload fields (optional; may be NULL/empty). */
    const char *message;
    const char *path;
    const char *component_id;

    dsu_u32 status_code;
    dsu_u64 digest64_a;
    dsu_u64 digest64_b;
    dsu_u64 digest64_c;
} dsu_log_event_t;

DSU_API void dsu_log_event_init(dsu_log_event_t *ev);

DSU_API dsu_status_t dsu_log_create(dsu_ctx_t *ctx, dsu_log_t **out_log);
DSU_API void dsu_log_destroy(dsu_ctx_t *ctx, dsu_log_t *log);
DSU_API dsu_status_t dsu_log_reset(dsu_ctx_t *ctx, dsu_log_t *log);

/* Open a new log context bound to an output path; close writes and destroys. */
DSU_API dsu_status_t dsu_log_open(dsu_ctx_t *ctx, const char *path, dsu_log_t **out_log);
DSU_API dsu_status_t dsu_log_close(dsu_ctx_t *ctx, dsu_log_t *log);

/* Structured event emission (v2). */
DSU_API dsu_status_t dsu_log_event(dsu_ctx_t *ctx, dsu_log_t *log, const dsu_log_event_t *ev);

/* Returns digest64 of the last successful write (0 if none). */
DSU_API dsu_bool dsu_log_has_last_written_digest64(const dsu_log_t *log);
DSU_API dsu_u64 dsu_log_last_written_digest64(const dsu_log_t *log);

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
DSU_API dsu_status_t dsu_log_export_json(dsu_ctx_t *ctx, const char *path, const char *out_json_path);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LOG_H_INCLUDED */
