/*
FILE: source/dominium/setup/core/include/dsu/dsu_resolve.h
MODULE: Dominium Setup
PURPOSE: Resolve requests to a canonical resolved component set (stub for Plan S-1).
*/
#ifndef DSU_RESOLVE_H_INCLUDED
#define DSU_RESOLVE_H_INCLUDED

#include "dsu_manifest.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_resolved dsu_resolved_t;

DSU_API dsu_status_t dsu_resolve(dsu_ctx_t *ctx,
                                const dsu_manifest_t *manifest,
                                dsu_resolved_t **out_resolved);

DSU_API void dsu_resolved_destroy(dsu_ctx_t *ctx, dsu_resolved_t *resolved);

DSU_API dsu_u32 dsu_resolved_component_count(const dsu_resolved_t *resolved);
DSU_API const char *dsu_resolved_component_id(const dsu_resolved_t *resolved, dsu_u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_RESOLVE_H_INCLUDED */

