/*
FILE: source/dominium/setup/core/include/dsu/dsu_execute.h
MODULE: Dominium Setup
PURPOSE: Plan execution entry points (DRY_RUN only for Plan S-1).
*/
#ifndef DSU_EXECUTE_H_INCLUDED
#define DSU_EXECUTE_H_INCLUDED

#include "dsu_plan.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsu_execute_mode_t {
    DSU_EXECUTE_MODE_DRY_RUN = 0
} dsu_execute_mode_t;

typedef struct dsu_execute_options_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;
    dsu_execute_mode_t mode;
    dsu_u32 reserved;
    const char *log_path;
} dsu_execute_options_t;

DSU_API void dsu_execute_options_init(dsu_execute_options_t *opts);

DSU_API dsu_status_t dsu_execute_plan(dsu_ctx_t *ctx,
                                     const dsu_plan_t *plan,
                                     const dsu_execute_options_t *opts);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_EXECUTE_H_INCLUDED */

