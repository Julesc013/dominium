/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/include/dsu_legacy_core.h
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Minimal Classic-compatible legacy core API (C89-friendly).
*/
#ifndef DSU_LEGACY_CORE_H_INCLUDED
#define DSU_LEGACY_CORE_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

typedef unsigned char dsu_legacy_u8;
typedef unsigned short dsu_legacy_u16;
typedef unsigned long dsu_legacy_u32;
typedef unsigned long dsu_legacy_u64;

typedef enum dsu_legacy_status_t {
    DSU_LEGACY_STATUS_SUCCESS = 0,
    DSU_LEGACY_STATUS_INVALID_ARGS = 1,
    DSU_LEGACY_STATUS_IO_ERROR = 2,
    DSU_LEGACY_STATUS_PARSE_ERROR = 3,
    DSU_LEGACY_STATUS_INTEGRITY_ERROR = 4,
    DSU_LEGACY_STATUS_UNSUPPORTED = 5,
    DSU_LEGACY_STATUS_NOT_FOUND = 6
} dsu_legacy_status_t;

typedef enum dsu_legacy_operation_t {
    DSU_LEGACY_OPERATION_INSTALL = 0,
    DSU_LEGACY_OPERATION_UPGRADE = 1,
    DSU_LEGACY_OPERATION_REPAIR = 2,
    DSU_LEGACY_OPERATION_UNINSTALL = 3
} dsu_legacy_operation_t;

typedef enum dsu_legacy_scope_t {
    DSU_LEGACY_SCOPE_PORTABLE = 0,
    DSU_LEGACY_SCOPE_USER = 1,
    DSU_LEGACY_SCOPE_SYSTEM = 2
} dsu_legacy_scope_t;

/* Policy flag bits (mirror DSU invocation policy flags). */
#define DSU_LEGACY_POLICY_OFFLINE           0x00000001u
#define DSU_LEGACY_POLICY_DETERMINISTIC     0x00000002u
#define DSU_LEGACY_POLICY_ALLOW_PRERELEASE  0x00000004u
#define DSU_LEGACY_POLICY_LEGACY_MODE       0x00000008u
#define DSU_LEGACY_POLICY_ENABLE_SHORTCUTS  0x00000010u
#define DSU_LEGACY_POLICY_ENABLE_FILE_ASSOC 0x00000020u
#define DSU_LEGACY_POLICY_ENABLE_URL_HANDLERS 0x00000040u

typedef enum dsu_legacy_payload_kind_t {
    DSU_LEGACY_PAYLOAD_FILESET = 0,
    DSU_LEGACY_PAYLOAD_ARCHIVE = 1,
    DSU_LEGACY_PAYLOAD_BLOB = 2
} dsu_legacy_payload_kind_t;

typedef struct dsu_legacy_invocation_t {
    dsu_legacy_u8 operation;
    dsu_legacy_u8 scope;
    dsu_legacy_u32 policy_flags;
    char *platform_triple;
    char *ui_mode;
    char *frontend_id;

    char **install_roots;
    dsu_legacy_u32 install_root_count;
    dsu_legacy_u32 install_root_cap;

    char **selected_components;
    dsu_legacy_u32 selected_component_count;
    dsu_legacy_u32 selected_component_cap;

    char **excluded_components;
    dsu_legacy_u32 excluded_component_count;
    dsu_legacy_u32 excluded_component_cap;
} dsu_legacy_invocation_t;

typedef struct dsu_legacy_manifest_payload_t {
    dsu_legacy_u8 kind;
    char *path;
    dsu_legacy_u64 size;
} dsu_legacy_manifest_payload_t;

typedef struct dsu_legacy_manifest_component_t {
    char *id;
    char *version;
    dsu_legacy_u8 kind;
    dsu_legacy_u32 flags;

    dsu_legacy_manifest_payload_t *payloads;
    dsu_legacy_u32 payload_count;
    dsu_legacy_u32 payload_cap;
} dsu_legacy_manifest_component_t;

typedef struct dsu_legacy_manifest_install_root_t {
    dsu_legacy_u8 scope;
    char *platform;
    char *path;
} dsu_legacy_manifest_install_root_t;

typedef struct dsu_legacy_manifest_t {
    char *product_id;
    char *product_version;
    char **platform_targets;
    dsu_legacy_u32 platform_target_count;
    dsu_legacy_u32 platform_target_cap;

    dsu_legacy_manifest_install_root_t *install_roots;
    dsu_legacy_u32 install_root_count;
    dsu_legacy_u32 install_root_cap;

    dsu_legacy_manifest_component_t *components;
    dsu_legacy_u32 component_count;
    dsu_legacy_u32 component_cap;
} dsu_legacy_manifest_t;

typedef struct dsu_legacy_state_component_t {
    char *id;
    char *version;
} dsu_legacy_state_component_t;

typedef struct dsu_legacy_state_file_t {
    char *path;
    dsu_legacy_u64 size;
    dsu_legacy_u8 sha256[32];
    dsu_legacy_u8 has_size;
    dsu_legacy_u8 has_sha256;
} dsu_legacy_state_file_t;

typedef struct dsu_legacy_state_t {
    char *product_id;
    char *product_version;
    char *platform_triple;
    dsu_legacy_u8 scope;
    char *install_root;

    dsu_legacy_state_component_t *components;
    dsu_legacy_u32 component_count;
    dsu_legacy_u32 component_cap;

    dsu_legacy_state_file_t *files;
    dsu_legacy_u32 file_count;
    dsu_legacy_u32 file_cap;
} dsu_legacy_state_t;

dsu_legacy_status_t dsu_legacy_invocation_load(const char *path,
                                               dsu_legacy_invocation_t **out_invocation);
void dsu_legacy_invocation_free(dsu_legacy_invocation_t *invocation);

dsu_legacy_status_t dsu_legacy_manifest_load(const char *path,
                                             dsu_legacy_manifest_t **out_manifest);
void dsu_legacy_manifest_free(dsu_legacy_manifest_t *manifest);

dsu_legacy_status_t dsu_legacy_state_write(const dsu_legacy_state_t *state,
                                           const char *path);
dsu_legacy_status_t dsu_legacy_state_load(const char *path,
                                          dsu_legacy_state_t **out_state);
void dsu_legacy_state_free(dsu_legacy_state_t *state);
dsu_legacy_status_t dsu_legacy_state_add_component(dsu_legacy_state_t *state,
                                                   const char *id,
                                                   const char *version);
dsu_legacy_status_t dsu_legacy_state_add_file(dsu_legacy_state_t *state,
                                              const char *path,
                                              dsu_legacy_u64 size);

dsu_legacy_status_t dsu_legacy_apply(const dsu_legacy_manifest_t *manifest,
                                     const dsu_legacy_invocation_t *invocation,
                                     const char *payload_root,
                                     const char *state_path,
                                     const char *log_path);
dsu_legacy_status_t dsu_legacy_verify(const char *state_path,
                                      const char *log_path);
dsu_legacy_status_t dsu_legacy_uninstall(const char *state_path,
                                         const char *log_path);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LEGACY_CORE_H_INCLUDED */
