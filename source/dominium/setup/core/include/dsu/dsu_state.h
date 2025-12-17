/*
FILE: source/dominium/setup/core/include/dsu/dsu_state.h
MODULE: Dominium Setup
PURPOSE: Installed-state load/save (Plan S-3).
*/
#ifndef DSU_STATE_H_INCLUDED
#define DSU_STATE_H_INCLUDED

#include "dsu_manifest.h"

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

DSU_API const char *dsu_state_product_id(const dsu_state_t *state);
DSU_API const char *dsu_state_product_version(const dsu_state_t *state);
DSU_API const char *dsu_state_platform(const dsu_state_t *state);
DSU_API dsu_manifest_install_scope_t dsu_state_scope(const dsu_state_t *state);
DSU_API const char *dsu_state_install_root(const dsu_state_t *state);

DSU_API dsu_u32 dsu_state_component_count(const dsu_state_t *state);
DSU_API const char *dsu_state_component_id(const dsu_state_t *state, dsu_u32 index);
DSU_API const char *dsu_state_component_version(const dsu_state_t *state, dsu_u32 index);

/* Installed file list (Plan S-4). Paths are relative to install root (canonical '/'). */
DSU_API dsu_u32 dsu_state_file_count(const dsu_state_t *state);
DSU_API const char *dsu_state_file_path(const dsu_state_t *state, dsu_u32 index);
DSU_API dsu_u64 dsu_state_file_size(const dsu_state_t *state, dsu_u32 index);
DSU_API const dsu_u8 *dsu_state_file_sha256(const dsu_state_t *state, dsu_u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_STATE_H_INCLUDED */
