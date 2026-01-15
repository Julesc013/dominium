/*
FILE: include/dsu/dsu_platform_iface.h
MODULE: Dominium Setup
PURPOSE: Platform adapter interface for declarative registrations and privileged operations (Plan S-6).
*/
#ifndef DSU_PLATFORM_IFACE_PUBLIC_H_INCLUDED
#define DSU_PLATFORM_IFACE_PUBLIC_H_INCLUDED

#include "dsu/dsu_ctx.h"
#include "dsu/dsu_state.h"
#include "dsu/dsu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DSU_PLATFORM_IFACE_VERSION 1u

typedef enum dsu_platform_intent_kind_t {
    DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY = 0,
    DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC = 1,
    DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER = 2,
    DSU_PLATFORM_INTENT_REGISTER_UNINSTALL_ENTRY = 3,
    DSU_PLATFORM_INTENT_DECLARE_CAPABILITY = 4
} dsu_platform_intent_kind_t;

/*
Intent is an OS-agnostic description of a platform registration action.

All string fields are UTF-8 C strings. Path fields are canonical DSU paths using '/' separators.

Lifetime: all pointers are owned by the caller of the adapter function and are valid only for the duration
of the call (adapters must copy if they need to retain).
*/
typedef struct dsu_platform_intent_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_u8 kind; /* dsu_platform_intent_kind_t */
    dsu_u8 reserved8[3];

    const char *component_id; /* optional context */

    const char *app_id;          /* ID */
    const char *display_name;    /* UTF-8 */
    const char *exec_relpath;    /* path */
    const char *arguments;       /* UTF-8 */
    const char *icon_relpath;    /* path */
    const char *extension;       /* e.g. ".domsave" */
    const char *protocol;        /* e.g. "dominium" */
    const char *marker_relpath;  /* path */
    const char *capability_id;   /* ID */
    const char *capability_value;/* UTF-8 */
    const char *publisher;       /* UTF-8 */
} dsu_platform_intent_t;

typedef struct dsu_platform_registrations_state_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    const char *product_id;
    const char *product_version;
    const char *build_channel;
    const char *platform_triple;
    dsu_u8 scope; /* dsu_manifest_install_scope_t */
    dsu_u8 reserved8[3];

    const char *install_root; /* primary install root (absolute canonical DSU path) */

    dsu_u32 intent_count;
    const dsu_platform_intent_t *intents;
} dsu_platform_registrations_state_t;

typedef struct dsu_platform_iface_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_status_t (*plat_request_elevation)(void *user, dsu_ctx_t *ctx);

    dsu_status_t (*plat_register_app_entry)(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
    dsu_status_t (*plat_register_file_assoc)(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
    dsu_status_t (*plat_register_url_handler)(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
    dsu_status_t (*plat_register_uninstall_entry)(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
    dsu_status_t (*plat_declare_capability)(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);

    dsu_status_t (*plat_remove_registrations)(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state);

    dsu_status_t (*plat_atomic_dir_swap)(void *user, dsu_ctx_t *ctx, const char *src_abs, const char *dst_abs);
    dsu_status_t (*plat_flush_fs)(void *user, dsu_ctx_t *ctx);

    dsu_u32 reserved[4];
} dsu_platform_iface_t;

DSU_API void dsu_platform_intent_init(dsu_platform_intent_t *intent);
DSU_API void dsu_platform_iface_init(dsu_platform_iface_t *iface);

/* Attach/detach platform interface to a context (ctx holds a copy). */
DSU_API dsu_status_t dsu_ctx_set_platform_iface(dsu_ctx_t *ctx,
                                                const dsu_platform_iface_t *iface,
                                                void *iface_user);

/* Dispatch helpers (fail with DSU_STATUS_INVALID_REQUEST if not provided). */
DSU_API dsu_status_t plat_request_elevation(dsu_ctx_t *ctx);
DSU_API dsu_status_t plat_register_app_entry(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
DSU_API dsu_status_t plat_register_file_assoc(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
DSU_API dsu_status_t plat_register_url_handler(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
DSU_API dsu_status_t plat_register_uninstall_entry(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
DSU_API dsu_status_t plat_declare_capability(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent);
DSU_API dsu_status_t plat_remove_registrations(dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state);
DSU_API dsu_status_t plat_atomic_dir_swap(dsu_ctx_t *ctx, const char *src_abs, const char *dst_abs);
DSU_API dsu_status_t plat_flush_fs(dsu_ctx_t *ctx);

/*
High-level helpers used by adapters/CLI.

Reads per-component registration intents from the installed state and invokes the platform interface.
These operations are deterministic and do not implement retries or heuristics.
*/
DSU_API dsu_status_t dsu_platform_register_from_state(dsu_ctx_t *ctx, const dsu_state_t *state);
DSU_API dsu_status_t dsu_platform_unregister_from_state(dsu_ctx_t *ctx, const dsu_state_t *state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_PLATFORM_IFACE_PUBLIC_H_INCLUDED */

