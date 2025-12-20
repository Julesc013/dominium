/*
FILE: source/dominium/setup/core/include/dsu/dsu_callbacks.h
MODULE: Dominium Setup
PURPOSE: Host callbacks for logging and progress reporting.
*/
#ifndef DSU_CALLBACKS_H_INCLUDED
#define DSU_CALLBACKS_H_INCLUDED

#include "dsu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DSU_CALLBACKS_VERSION 1u

typedef enum dsu_log_severity_t {
    DSU_LOG_SEVERITY_DEBUG = 0,
    DSU_LOG_SEVERITY_INFO = 1,
    DSU_LOG_SEVERITY_WARN = 2,
    DSU_LOG_SEVERITY_ERROR = 3
} dsu_log_severity_t;

typedef enum dsu_log_category_t {
    DSU_LOG_CATEGORY_GENERAL = 0,
    DSU_LOG_CATEGORY_MANIFEST = 1,
    DSU_LOG_CATEGORY_RESOLVE = 2,
    DSU_LOG_CATEGORY_PLAN = 3,
    DSU_LOG_CATEGORY_EXECUTE = 4,
    DSU_LOG_CATEGORY_IO = 5
} dsu_log_category_t;

typedef void (*dsu_log_callback_t)(void *user,
                                  dsu_u32 event_id,
                                  dsu_u8 severity,
                                  dsu_u8 category,
                                  dsu_u32 timestamp,
                                  const char *message);

typedef void (*dsu_progress_callback_t)(void *user,
                                       dsu_u32 current,
                                       dsu_u32 total,
                                       const char *phase);

typedef struct dsu_callbacks_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;
    dsu_log_callback_t log;
    dsu_progress_callback_t progress;
    dsu_u32 reserved[4];
} dsu_callbacks_t;

DSU_API void dsu_callbacks_init(dsu_callbacks_t *cbs);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_CALLBACKS_H_INCLUDED */

