/*
FILE: source/dominium/setup/core/include/dsu/dsu_state.h
MODULE: Dominium Setup
PURPOSE: Installed-state load/save stubs (Plan S-1 foundation).
*/
#ifndef DSU_STATE_H_INCLUDED
#define DSU_STATE_H_INCLUDED

#include "dsu_ctx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_state dsu_state_t;

DSU_API dsu_status_t dsu_state_load_file(dsu_ctx_t *ctx,
                                        const char *path,
                                        dsu_state_t **out_state);

DSU_API dsu_status_t dsu_state_write_file(dsu_ctx_t *ctx,
                                         const dsu_state_t *state,
                                         const char *path);

DSU_API void dsu_state_destroy(dsu_ctx_t *ctx, dsu_state_t *state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_STATE_H_INCLUDED */

