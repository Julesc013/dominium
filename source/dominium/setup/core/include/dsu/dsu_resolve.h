/*
FILE: source/dominium/setup/core/include/dsu/dsu_resolve.h
MODULE: Dominium Setup
PURPOSE: Deterministic component resolution (Plan S-3).
*/
#ifndef DSU_RESOLVE_H_INCLUDED
#define DSU_RESOLVE_H_INCLUDED

#include "dsu_manifest.h"
#include "dsu_state.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsu_resolve_operation_t {
    DSU_RESOLVE_OPERATION_INSTALL = 0,
    DSU_RESOLVE_OPERATION_UPGRADE = 1,
    DSU_RESOLVE_OPERATION_REPAIR = 2,
    DSU_RESOLVE_OPERATION_UNINSTALL = 3
} dsu_resolve_operation_t;

typedef enum dsu_resolve_source_t {
    DSU_RESOLVE_SOURCE_DEFAULT = 0,
    DSU_RESOLVE_SOURCE_USER = 1,
    DSU_RESOLVE_SOURCE_DEPENDENCY = 2,
    DSU_RESOLVE_SOURCE_INSTALLED = 3
} dsu_resolve_source_t;

typedef enum dsu_resolve_component_action_t {
    DSU_RESOLVE_COMPONENT_ACTION_NONE = 0,
    DSU_RESOLVE_COMPONENT_ACTION_INSTALL = 1,
    DSU_RESOLVE_COMPONENT_ACTION_UPGRADE = 2,
    DSU_RESOLVE_COMPONENT_ACTION_REPAIR = 3,
    DSU_RESOLVE_COMPONENT_ACTION_UNINSTALL = 4
} dsu_resolve_component_action_t;

typedef enum dsu_resolve_log_code_t {
    DSU_RESOLVE_LOG_SEED_USER = 0,
    DSU_RESOLVE_LOG_SEED_DEFAULT = 1,
    DSU_RESOLVE_LOG_ADD_DEPENDENCY = 2,
    DSU_RESOLVE_LOG_CONFLICT = 3,
    DSU_RESOLVE_LOG_PLATFORM_FILTER = 4,
    DSU_RESOLVE_LOG_RECONCILE_INSTALLED = 5
} dsu_resolve_log_code_t;

typedef struct dsu_invocation_t dsu_invocation_t;

typedef struct dsu_resolve_pin_t {
    const char *component_id;
    const char *version;
} dsu_resolve_pin_t;

typedef struct dsu_resolve_request_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_resolve_operation_t operation;
    dsu_manifest_install_scope_t scope;
    dsu_bool allow_prerelease;

    /* Optional: explicit target platform triple (NULL/empty => manifest-preferred). */
    const char *target_platform;

    /* Optional: explicit install roots (count <= 1 in current core). */
    const char *const *install_roots;
    dsu_u32 install_root_count;

    /* Explicit user selection and exclusions (IDs; may be mixed-case). */
    const char *const *requested_components;
    dsu_u32 requested_component_count;
    const char *const *excluded_components;
    dsu_u32 excluded_component_count;

    /* Optional version pinning rules (minimal in Plan S-3). */
    const dsu_resolve_pin_t *pins;
    dsu_u32 pin_count;
} dsu_resolve_request_t;

DSU_API void dsu_resolve_request_init(dsu_resolve_request_t *req);

typedef struct dsu_resolve_result dsu_resolve_result_t;

DSU_API dsu_status_t dsu_resolve_components(dsu_ctx_t *ctx,
                                           const dsu_manifest_t *manifest,
                                           const dsu_state_t *installed_state,
                                           const dsu_resolve_request_t *request,
                                           dsu_resolve_result_t **out_result);

DSU_API dsu_status_t dsu_resolve_components_from_invocation(dsu_ctx_t *ctx,
                                                           const dsu_manifest_t *manifest,
                                                           const dsu_state_t *installed_state,
                                                           const dsu_invocation_t *invocation,
                                                           dsu_resolve_result_t **out_result,
                                                           dsu_u64 *out_invocation_digest);

DSU_API void dsu_resolve_result_destroy(dsu_ctx_t *ctx, dsu_resolve_result_t *result);

DSU_API dsu_resolve_operation_t dsu_resolve_result_operation(const dsu_resolve_result_t *result);
DSU_API dsu_manifest_install_scope_t dsu_resolve_result_scope(const dsu_resolve_result_t *result);
DSU_API const char *dsu_resolve_result_platform(const dsu_resolve_result_t *result);

DSU_API const char *dsu_resolve_result_product_id(const dsu_resolve_result_t *result);
DSU_API const char *dsu_resolve_result_product_version(const dsu_resolve_result_t *result);
DSU_API const char *dsu_resolve_result_install_root(const dsu_resolve_result_t *result);

DSU_API dsu_u64 dsu_resolve_result_manifest_digest64(const dsu_resolve_result_t *result);
DSU_API dsu_u64 dsu_resolve_result_resolved_digest64(const dsu_resolve_result_t *result);

DSU_API dsu_u32 dsu_resolve_result_component_count(const dsu_resolve_result_t *result);
DSU_API const char *dsu_resolve_result_component_id(const dsu_resolve_result_t *result, dsu_u32 index);
DSU_API const char *dsu_resolve_result_component_version(const dsu_resolve_result_t *result, dsu_u32 index);
DSU_API dsu_resolve_source_t dsu_resolve_result_component_source(const dsu_resolve_result_t *result, dsu_u32 index);
DSU_API dsu_resolve_component_action_t dsu_resolve_result_component_action(const dsu_resolve_result_t *result, dsu_u32 index);

DSU_API dsu_u32 dsu_resolve_result_log_count(const dsu_resolve_result_t *result);
DSU_API dsu_resolve_log_code_t dsu_resolve_result_log_code(const dsu_resolve_result_t *result, dsu_u32 index);
DSU_API const char *dsu_resolve_result_log_a(const dsu_resolve_result_t *result, dsu_u32 index);
DSU_API const char *dsu_resolve_result_log_b(const dsu_resolve_result_t *result, dsu_u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_RESOLVE_H_INCLUDED */
