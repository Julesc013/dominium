/*
FILE: source/dominium/setup/core/include/dsu/dsu_manifest.h
MODULE: Dominium Setup
PURPOSE: Manifest loading/validation (TLV binary manifest for Plan S-2).
*/
#ifndef DSU_MANIFEST_H_INCLUDED
#define DSU_MANIFEST_H_INCLUDED

#include "dsu_ctx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_manifest dsu_manifest_t;

#define DSU_MANIFEST_MAGIC_0 'D'
#define DSU_MANIFEST_MAGIC_1 'S'
#define DSU_MANIFEST_MAGIC_2 'U'
#define DSU_MANIFEST_MAGIC_3 'M'

/* DSUM file format version for TLV manifests (Plan S-2). */
#define DSU_MANIFEST_FORMAT_VERSION 2u

/* Root schema version (inside the TLV root container). */
#define DSU_MANIFEST_ROOT_SCHEMA_VERSION 1u

typedef enum dsu_manifest_install_scope_t {
    DSU_MANIFEST_INSTALL_SCOPE_PORTABLE = 0,
    DSU_MANIFEST_INSTALL_SCOPE_USER = 1,
    DSU_MANIFEST_INSTALL_SCOPE_SYSTEM = 2
} dsu_manifest_install_scope_t;

typedef enum dsu_manifest_component_kind_t {
    DSU_MANIFEST_COMPONENT_KIND_LAUNCHER = 0,
    DSU_MANIFEST_COMPONENT_KIND_RUNTIME = 1,
    DSU_MANIFEST_COMPONENT_KIND_TOOLS = 2,
    DSU_MANIFEST_COMPONENT_KIND_PACK = 3,
    DSU_MANIFEST_COMPONENT_KIND_DRIVER = 4,
    DSU_MANIFEST_COMPONENT_KIND_OTHER = 5
} dsu_manifest_component_kind_t;

typedef enum dsu_manifest_payload_kind_t {
    DSU_MANIFEST_PAYLOAD_KIND_FILESET = 0,
    DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE = 1,
    DSU_MANIFEST_PAYLOAD_KIND_BLOB = 2
} dsu_manifest_payload_kind_t;

typedef enum dsu_manifest_version_constraint_kind_t {
    DSU_MANIFEST_VERSION_CONSTRAINT_ANY = 0,
    DSU_MANIFEST_VERSION_CONSTRAINT_EXACT = 1,
    DSU_MANIFEST_VERSION_CONSTRAINT_AT_LEAST = 2
} dsu_manifest_version_constraint_kind_t;

typedef enum dsu_manifest_action_kind_t {
    DSU_MANIFEST_ACTION_REGISTER_APP_ENTRY = 0,
    DSU_MANIFEST_ACTION_REGISTER_FILE_ASSOC = 1,
    DSU_MANIFEST_ACTION_REGISTER_URL_HANDLER = 2,
    DSU_MANIFEST_ACTION_REGISTER_UNINSTALL_ENTRY = 3,
    DSU_MANIFEST_ACTION_WRITE_FIRST_RUN_MARKER = 4,
    DSU_MANIFEST_ACTION_DECLARE_CAPABILITY = 5
} dsu_manifest_action_kind_t;

/* Component flags */
#define DSU_MANIFEST_COMPONENT_FLAG_OPTIONAL          0x00000001u
#define DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED  0x00000002u
#define DSU_MANIFEST_COMPONENT_FLAG_HIDDEN            0x00000004u

DSU_API dsu_status_t dsu_manifest_load_file(dsu_ctx_t *ctx,
                                           const char *path,
                                           dsu_manifest_t **out_manifest);

DSU_API void dsu_manifest_destroy(dsu_ctx_t *ctx, dsu_manifest_t *manifest);

DSU_API const char *dsu_manifest_product_id(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_product_version(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_build_channel(const dsu_manifest_t *manifest);

/* Compatibility accessors (Plan S-1 naming). */
DSU_API const char *dsu_manifest_version(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_install_root(const dsu_manifest_t *manifest);

DSU_API dsu_u32 dsu_manifest_content_digest32(const dsu_manifest_t *manifest);
DSU_API dsu_u64 dsu_manifest_content_digest64(const dsu_manifest_t *manifest);

DSU_API dsu_u32 dsu_manifest_component_count(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_component_id(const dsu_manifest_t *manifest, dsu_u32 index);

/* Component metadata (Plan S-3 resolution). */
DSU_API const char *dsu_manifest_component_version(const dsu_manifest_t *manifest, dsu_u32 index);
DSU_API dsu_manifest_component_kind_t dsu_manifest_component_kind(const dsu_manifest_t *manifest, dsu_u32 index);
DSU_API dsu_u32 dsu_manifest_component_flags(const dsu_manifest_t *manifest, dsu_u32 index);

/* Payloads (sorted deterministically by manifest canonicalization). */
DSU_API dsu_u32 dsu_manifest_component_payload_count(const dsu_manifest_t *manifest, dsu_u32 component_index);
DSU_API dsu_manifest_payload_kind_t dsu_manifest_component_payload_kind(const dsu_manifest_t *manifest,
                                                                       dsu_u32 component_index,
                                                                       dsu_u32 payload_index);
DSU_API const char *dsu_manifest_component_payload_path(const dsu_manifest_t *manifest,
                                                       dsu_u32 component_index,
                                                       dsu_u32 payload_index);
DSU_API const dsu_u8 *dsu_manifest_component_payload_sha256(const dsu_manifest_t *manifest,
                                                          dsu_u32 component_index,
                                                          dsu_u32 payload_index);
DSU_API dsu_u64 dsu_manifest_component_payload_size(const dsu_manifest_t *manifest,
                                                  dsu_u32 component_index,
                                                  dsu_u32 payload_index,
                                                  dsu_bool *out_present);

/* Actions (sorted deterministically by manifest canonicalization). */
DSU_API dsu_u32 dsu_manifest_component_action_count(const dsu_manifest_t *manifest, dsu_u32 component_index);
DSU_API dsu_manifest_action_kind_t dsu_manifest_component_action_kind(const dsu_manifest_t *manifest,
                                                                     dsu_u32 component_index,
                                                                     dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_app_id(const dsu_manifest_t *manifest,
                                                        dsu_u32 component_index,
                                                        dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_display_name(const dsu_manifest_t *manifest,
                                                              dsu_u32 component_index,
                                                              dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_exec_relpath(const dsu_manifest_t *manifest,
                                                              dsu_u32 component_index,
                                                              dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_arguments(const dsu_manifest_t *manifest,
                                                           dsu_u32 component_index,
                                                           dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_icon_relpath(const dsu_manifest_t *manifest,
                                                              dsu_u32 component_index,
                                                              dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_extension(const dsu_manifest_t *manifest,
                                                           dsu_u32 component_index,
                                                           dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_protocol(const dsu_manifest_t *manifest,
                                                          dsu_u32 component_index,
                                                          dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_marker_relpath(const dsu_manifest_t *manifest,
                                                                dsu_u32 component_index,
                                                                dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_capability_id(const dsu_manifest_t *manifest,
                                                               dsu_u32 component_index,
                                                               dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_capability_value(const dsu_manifest_t *manifest,
                                                                  dsu_u32 component_index,
                                                                  dsu_u32 action_index);
DSU_API const char *dsu_manifest_component_action_publisher(const dsu_manifest_t *manifest,
                                                           dsu_u32 component_index,
                                                           dsu_u32 action_index);

/* Dependencies (sorted deterministically by manifest canonicalization). */
DSU_API dsu_u32 dsu_manifest_component_dependency_count(const dsu_manifest_t *manifest, dsu_u32 component_index);
DSU_API const char *dsu_manifest_component_dependency_id(const dsu_manifest_t *manifest,
                                                        dsu_u32 component_index,
                                                        dsu_u32 dependency_index);
DSU_API dsu_manifest_version_constraint_kind_t dsu_manifest_component_dependency_constraint_kind(const dsu_manifest_t *manifest,
                                                                                               dsu_u32 component_index,
                                                                                               dsu_u32 dependency_index);
DSU_API const char *dsu_manifest_component_dependency_constraint_version(const dsu_manifest_t *manifest,
                                                                       dsu_u32 component_index,
                                                                       dsu_u32 dependency_index);

/* Conflicts (sorted deterministically by manifest canonicalization). */
DSU_API dsu_u32 dsu_manifest_component_conflict_count(const dsu_manifest_t *manifest, dsu_u32 component_index);
DSU_API const char *dsu_manifest_component_conflict_id(const dsu_manifest_t *manifest,
                                                      dsu_u32 component_index,
                                                      dsu_u32 conflict_index);

/* Platforms and install roots (sorted deterministically by manifest canonicalization). */
DSU_API dsu_u32 dsu_manifest_platform_target_count(const dsu_manifest_t *manifest);
DSU_API const char *dsu_manifest_platform_target(const dsu_manifest_t *manifest, dsu_u32 index);

DSU_API dsu_u32 dsu_manifest_install_root_count(const dsu_manifest_t *manifest);
DSU_API dsu_manifest_install_scope_t dsu_manifest_install_root_scope(const dsu_manifest_t *manifest, dsu_u32 index);
DSU_API const char *dsu_manifest_install_root_platform(const dsu_manifest_t *manifest, dsu_u32 index);
DSU_API const char *dsu_manifest_install_root_path(const dsu_manifest_t *manifest, dsu_u32 index);

/* Canonical writer utilities (TLV is always canonical output). */
DSU_API dsu_status_t dsu_manifest_write_file(dsu_ctx_t *ctx,
                                            const dsu_manifest_t *manifest,
                                            const char *path);
DSU_API dsu_status_t dsu_manifest_write_json_file(dsu_ctx_t *ctx,
                                                 const dsu_manifest_t *manifest,
                                                 const char *path);

/* Explicit validation/canonicalization (load() already enforces these). */
DSU_API dsu_status_t dsu_manifest_validate(const dsu_manifest_t *manifest);
DSU_API dsu_status_t dsu_manifest_canonicalize(dsu_manifest_t *manifest);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_MANIFEST_H_INCLUDED */
