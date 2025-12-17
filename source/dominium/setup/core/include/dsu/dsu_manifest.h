/*
FILE: source/dominium/setup/core/include/dsu/dsu_manifest.h
MODULE: Dominium Setup
PURPOSE: Manifest loading/validation (baseline format for Plan S-1).
*/
#ifndef DSU_MANIFEST_H_INCLUDED
#define DSU_MANIFEST_H_INCLUDED

#include "dsu_ctx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_manifest dsu_manifest_t;

DSU_API dsu_status_t dsu_manifest_load_file(dsu_ctx_t *ctx,
                                           const char *path,
                                           dsu_manifest_t **out_manifest);

DSU_API void dsu_manifest_destroy(dsu_ctx_t *ctx, dsu_manifest_t *manifest);

DSU_API const char *dsu_manifest_product_id(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_version(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_install_root(const dsu_manifest_t *manifest);

DSU_API dsu_u32 dsu_manifest_component_count(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_component_id(const dsu_manifest_t *manifest, dsu_u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_MANIFEST_H_INCLUDED */

