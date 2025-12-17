/*
FILE: source/dominium/setup/core/include/dsu/dsu_plan.h
MODULE: Dominium Setup
PURPOSE: Plan building and deterministic (de)serialization.
*/
#ifndef DSU_PLAN_H_INCLUDED
#define DSU_PLAN_H_INCLUDED

#include "dsu_resolve.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_plan dsu_plan_t;

typedef enum dsu_plan_step_kind_t {
    DSU_PLAN_STEP_DECLARE_INSTALL_ROOT = 0,
    DSU_PLAN_STEP_INSTALL_COMPONENT = 1,
    DSU_PLAN_STEP_WRITE_STATE = 2,
    DSU_PLAN_STEP_WRITE_LOG = 3,
    DSU_PLAN_STEP_UPGRADE_COMPONENT = 4,
    DSU_PLAN_STEP_REPAIR_COMPONENT = 5,
    DSU_PLAN_STEP_UNINSTALL_COMPONENT = 6
} dsu_plan_step_kind_t;

/*
Build a deterministic plan from a manifest + resolved selection.

Plan S-4: The plan includes explicit filesystem intents (directories + file list)
derived from local payloads referenced by the manifest.
*/
DSU_API dsu_status_t dsu_plan_build(dsu_ctx_t *ctx,
                                   const dsu_manifest_t *manifest,
                                   const char *manifest_path,
                                   const dsu_resolve_result_t *resolved,
                                   dsu_plan_t **out_plan);

DSU_API void dsu_plan_destroy(dsu_ctx_t *ctx, dsu_plan_t *plan);

DSU_API dsu_u32 dsu_plan_id_hash32(const dsu_plan_t *plan);
DSU_API dsu_u64 dsu_plan_id_hash64(const dsu_plan_t *plan);

DSU_API dsu_resolve_operation_t dsu_plan_operation(const dsu_plan_t *plan);
DSU_API dsu_manifest_install_scope_t dsu_plan_scope(const dsu_plan_t *plan);

DSU_API const char *dsu_plan_product_id(const dsu_plan_t *plan);
DSU_API const char *dsu_plan_version(const dsu_plan_t *plan);
DSU_API const char *dsu_plan_platform(const dsu_plan_t *plan);
DSU_API const char *dsu_plan_install_root(const dsu_plan_t *plan);

DSU_API dsu_u32 dsu_plan_component_count(const dsu_plan_t *plan);
DSU_API const char *dsu_plan_component_id(const dsu_plan_t *plan, dsu_u32 index);
DSU_API const char *dsu_plan_component_version(const dsu_plan_t *plan, dsu_u32 index);

DSU_API dsu_u32 dsu_plan_step_count(const dsu_plan_t *plan);
DSU_API dsu_plan_step_kind_t dsu_plan_step_kind(const dsu_plan_t *plan, dsu_u32 index);
DSU_API const char *dsu_plan_step_arg(const dsu_plan_t *plan, dsu_u32 index);

/* Explicit filesystem intents (Plan S-4). All paths are relative to install root (canonical '/'). */
DSU_API dsu_u32 dsu_plan_dir_count(const dsu_plan_t *plan);
DSU_API const char *dsu_plan_dir_path(const dsu_plan_t *plan, dsu_u32 index);

DSU_API dsu_u32 dsu_plan_file_count(const dsu_plan_t *plan);
DSU_API const char *dsu_plan_file_target_path(const dsu_plan_t *plan, dsu_u32 index);
DSU_API dsu_manifest_payload_kind_t dsu_plan_file_source_kind(const dsu_plan_t *plan, dsu_u32 index);
DSU_API const char *dsu_plan_file_source_container_path(const dsu_plan_t *plan, dsu_u32 index);
DSU_API const char *dsu_plan_file_source_member_path(const dsu_plan_t *plan, dsu_u32 index);
DSU_API dsu_u64 dsu_plan_file_size(const dsu_plan_t *plan, dsu_u32 index);
DSU_API const dsu_u8 *dsu_plan_file_sha256(const dsu_plan_t *plan, dsu_u32 index);

DSU_API dsu_status_t dsu_plan_write_file(dsu_ctx_t *ctx, const dsu_plan_t *plan, const char *path);
DSU_API dsu_status_t dsu_plan_read_file(dsu_ctx_t *ctx, const char *path, dsu_plan_t **out_plan);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_PLAN_H_INCLUDED */
