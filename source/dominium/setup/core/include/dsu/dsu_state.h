/*
FILE: source/dominium/setup/core/include/dsu/dsu_state.h
MODULE: Dominium Setup
PURPOSE: Installed-state load/save + forensics (Plan S-5).
*/
#ifndef DSU_STATE_H_INCLUDED
#define DSU_STATE_H_INCLUDED

#include "dsu_manifest.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_state dsu_state_t;
typedef struct dsu_state_diff dsu_state_diff_t;

typedef enum dsu_state_install_root_role_t {
    DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY = 0,
    DSU_STATE_INSTALL_ROOT_ROLE_STATE = 1,
    DSU_STATE_INSTALL_ROOT_ROLE_CACHE = 2,
    DSU_STATE_INSTALL_ROOT_ROLE_USER_DATA = 3
} dsu_state_install_root_role_t;

typedef enum dsu_state_file_ownership_t {
    DSU_STATE_FILE_OWNERSHIP_OWNED = 0,
    DSU_STATE_FILE_OWNERSHIP_USER_DATA = 1,
    DSU_STATE_FILE_OWNERSHIP_CACHE = 2
} dsu_state_file_ownership_t;

typedef enum dsu_state_last_operation_t {
    DSU_STATE_OPERATION_INSTALL = 0,
    DSU_STATE_OPERATION_UPGRADE = 1,
    DSU_STATE_OPERATION_REPAIR = 2,
    DSU_STATE_OPERATION_UNINSTALL = 3
} dsu_state_last_operation_t;

/* File flags (u32). */
#define DSU_STATE_FILE_FLAG_CREATED_BY_INSTALL  0x00000001u
#define DSU_STATE_FILE_FLAG_MODIFIED_AFTER_INSTALL 0x00000002u

/* Core load/save/validate (installed state is the single authoritative record). */
DSU_API dsu_status_t dsu_state_load(dsu_ctx_t *ctx,
                                   const char *path,
                                   dsu_state_t **out_state);

DSU_API dsu_status_t dsu_state_save_atomic(dsu_ctx_t *ctx,
                                          const dsu_state_t *state,
                                          const char *path);

DSU_API dsu_status_t dsu_state_validate(dsu_state_t *state);

DSU_API dsu_status_t dsu_state_diff(const dsu_state_t *old_state,
                                   const dsu_state_t *new_state,
                                   dsu_state_diff_t **out_diff);

DSU_API void dsu_state_diff_destroy(dsu_ctx_t *ctx, dsu_state_diff_t *diff);

DSU_API void dsu_state_destroy(dsu_ctx_t *ctx, dsu_state_t *state);

DSU_API const char *dsu_state_product_id(const dsu_state_t *state);
DSU_API const char *dsu_state_product_version_installed(const dsu_state_t *state);
DSU_API const char *dsu_state_build_channel(const dsu_state_t *state);
DSU_API const char *dsu_state_platform(const dsu_state_t *state);
DSU_API dsu_manifest_install_scope_t dsu_state_install_scope(const dsu_state_t *state);
DSU_API dsu_u64 dsu_state_install_instance_id(const dsu_state_t *state);

DSU_API dsu_u32 dsu_state_install_root_count(const dsu_state_t *state);
DSU_API dsu_state_install_root_role_t dsu_state_install_root_role(const dsu_state_t *state, dsu_u32 index);
DSU_API const char *dsu_state_install_root_path(const dsu_state_t *state, dsu_u32 index);
DSU_API const char *dsu_state_primary_install_root(const dsu_state_t *state);

DSU_API dsu_u64 dsu_state_manifest_digest64(const dsu_state_t *state);
DSU_API dsu_u64 dsu_state_resolved_set_digest64(const dsu_state_t *state);
DSU_API dsu_u64 dsu_state_plan_digest64(const dsu_state_t *state);

DSU_API dsu_state_last_operation_t dsu_state_last_successful_operation(const dsu_state_t *state);
DSU_API dsu_u64 dsu_state_last_journal_id(const dsu_state_t *state);
DSU_API dsu_bool dsu_state_has_last_audit_log_digest64(const dsu_state_t *state);
DSU_API dsu_u64 dsu_state_last_audit_log_digest64(const dsu_state_t *state);

DSU_API dsu_u32 dsu_state_component_count(const dsu_state_t *state);
DSU_API const char *dsu_state_component_id(const dsu_state_t *state, dsu_u32 index);
DSU_API const char *dsu_state_component_version(const dsu_state_t *state, dsu_u32 index);
DSU_API dsu_manifest_component_kind_t dsu_state_component_kind(const dsu_state_t *state, dsu_u32 index);
DSU_API dsu_u64 dsu_state_component_install_time_policy(const dsu_state_t *state, dsu_u32 index);

DSU_API dsu_u32 dsu_state_component_file_count(const dsu_state_t *state, dsu_u32 component_index);
DSU_API dsu_u32 dsu_state_component_file_root_index(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index);
DSU_API const char *dsu_state_component_file_path(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index);
DSU_API dsu_u64 dsu_state_component_file_size(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index);
DSU_API dsu_u64 dsu_state_component_file_digest64(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index);
DSU_API dsu_state_file_ownership_t dsu_state_component_file_ownership(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index);
DSU_API dsu_u32 dsu_state_component_file_flags(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index);

DSU_API dsu_u32 dsu_state_component_registration_count(const dsu_state_t *state, dsu_u32 component_index);
DSU_API const char *dsu_state_component_registration(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 reg_index);

DSU_API dsu_u32 dsu_state_component_marker_count(const dsu_state_t *state, dsu_u32 component_index);
DSU_API const char *dsu_state_component_marker(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 marker_index);

/* Compatibility API (S-3/S-4 naming). */
DSU_API dsu_status_t dsu_state_load_file(dsu_ctx_t *ctx,
                                        const char *path,
                                        dsu_state_t **out_state);
DSU_API dsu_status_t dsu_state_write_file(dsu_ctx_t *ctx,
                                         const dsu_state_t *state,
                                         const char *path);
DSU_API const char *dsu_state_product_version(const dsu_state_t *state);
DSU_API dsu_manifest_install_scope_t dsu_state_scope(const dsu_state_t *state);
DSU_API const char *dsu_state_install_root(const dsu_state_t *state);
DSU_API dsu_u32 dsu_state_file_count(const dsu_state_t *state);
DSU_API const char *dsu_state_file_path(const dsu_state_t *state, dsu_u32 index);
DSU_API dsu_u64 dsu_state_file_size(const dsu_state_t *state, dsu_u32 index);
DSU_API const dsu_u8 *dsu_state_file_sha256(const dsu_state_t *state, dsu_u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_STATE_H_INCLUDED */
