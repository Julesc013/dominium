/*
FILE: source/dominium/setup/core/include/dsu/dsu_invocation.h
MODULE: Dominium Setup
PURPOSE: Invocation payload load/validate/digest (installer UX contract input).
*/
#ifndef DSU_INVOCATION_H_INCLUDED
#define DSU_INVOCATION_H_INCLUDED

#include "dsu_ctx.h"
#include "dsu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsu_invocation_operation_t {
    DSU_INVOCATION_OPERATION_INSTALL = 0,
    DSU_INVOCATION_OPERATION_UPGRADE = 1,
    DSU_INVOCATION_OPERATION_REPAIR = 2,
    DSU_INVOCATION_OPERATION_UNINSTALL = 3
} dsu_invocation_operation_t;

typedef enum dsu_invocation_scope_t {
    DSU_INVOCATION_SCOPE_PORTABLE = 0,
    DSU_INVOCATION_SCOPE_USER = 1,
    DSU_INVOCATION_SCOPE_SYSTEM = 2
} dsu_invocation_scope_t;

/* Policy flag bits (see docs/setup/INVOCATION_PAYLOAD.md). */
#define DSU_INVOCATION_POLICY_OFFLINE         0x00000001u
#define DSU_INVOCATION_POLICY_DETERMINISTIC   0x00000002u
#define DSU_INVOCATION_POLICY_ALLOW_PRERELEASE 0x00000004u
#define DSU_INVOCATION_POLICY_LEGACY_MODE     0x00000008u
#define DSU_INVOCATION_POLICY_ENABLE_SHORTCUTS 0x00000010u
#define DSU_INVOCATION_POLICY_ENABLE_FILE_ASSOC 0x00000020u
#define DSU_INVOCATION_POLICY_ENABLE_URL_HANDLERS 0x00000040u

typedef struct dsu_invocation_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_u8 operation;
    dsu_u8 scope;
    dsu_u8 reserved8[2];

    dsu_u32 policy_flags;

    char *platform_triple;
    char *ui_mode;
    char *frontend_id;

    char **install_roots;
    dsu_u32 install_root_count;

    char **selected_components;
    dsu_u32 selected_component_count;

    char **excluded_components;
    dsu_u32 excluded_component_count;
} dsu_invocation_t;

DSU_API void dsu_invocation_init(dsu_invocation_t *inv);
DSU_API void dsu_invocation_destroy(dsu_ctx_t *ctx, dsu_invocation_t *inv);

DSU_API dsu_status_t dsu_invocation_load(dsu_ctx_t *ctx,
                                        const char *path,
                                        dsu_invocation_t **out_invocation);
DSU_API dsu_status_t dsu_invocation_write_file(dsu_ctx_t *ctx,
                                              const dsu_invocation_t *invocation,
                                              const char *path);

DSU_API dsu_status_t dsu_invocation_validate(const dsu_invocation_t *invocation);
DSU_API dsu_u64 dsu_invocation_digest(const dsu_invocation_t *invocation);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_INVOCATION_H_INCLUDED */
