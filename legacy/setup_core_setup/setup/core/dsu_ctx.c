/*
FILE: source/dominium/setup/core/src/dsu_ctx.c
MODULE: Dominium Setup
LAYER / SUBSYSTEM: Setup Core context implementation
RESPONSIBILITY:
  - Owns context allocation, initialization, and audit log setup/teardown.
  - Does not implement manifest/plan/execute logic or platform backends.
ALLOWED DEPENDENCIES: dsu_ctx.h, dsu_log.h, dsu_platform_iface.h, setup core internal headers.
FORBIDDEN DEPENDENCIES: Launcher/game subsystems; UI/renderer layers.
THREADING MODEL: Single-threaded; no internal threads.
ERROR MODEL: dsu_status_t codes for invalid args, allocation failures, and log init failures.
DETERMINISM GUARANTEES: Determinism is configured by dsu_config_t; this file adds no nondeterministic sources.
VERSIONING / ABI / DATA FORMAT NOTES: Validates struct_size/struct_version for config and callbacks.
EXTENSION POINTS: None.
*/
/*
FILE: source/dominium/setup/core/src/dsu_ctx.c
MODULE: Dominium Setup
PURPOSE: Setup Core context lifecycle implementation.
*/
#include "../include/dsu/dsu_ctx.h"
#include "../include/dsu/dsu_log.h"

#include "dsu/dsu_platform_iface.h"

#include "dsu_ctx_internal.h"
#include "util/dsu_util_internal.h"

static int dsu__validate_config(const dsu_config_t *cfg) {
    if (!cfg) {
        return 1;
    }
    /* Version/size checks gate ABI compatibility for callers. */
    if (cfg->struct_version != DSU_CONFIG_VERSION) {
        return 0;
    }
    if (cfg->struct_size < (dsu_u32)sizeof(dsu_config_t)) {
        return 0;
    }
    return 1;
}

static int dsu__validate_callbacks(const dsu_callbacks_t *cbs) {
    if (!cbs) {
        return 1;
    }
    /* Version/size checks gate ABI compatibility for callers. */
    if (cbs->struct_version != DSU_CALLBACKS_VERSION) {
        return 0;
    }
    if (cbs->struct_size < (dsu_u32)sizeof(dsu_callbacks_t)) {
        return 0;
    }
    return 1;
}

dsu_status_t dsu_ctx_create(const dsu_config_t *config,
                           const dsu_callbacks_t *callbacks,
                           void *callbacks_user,
                           dsu_ctx_t **out_ctx) {
    dsu_ctx_t *ctx;
    dsu_config_t cfg_local;
    dsu_callbacks_t cbs_local;
    dsu_status_t st;

    if (!out_ctx) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_ctx = NULL;

    if (!dsu__validate_config(config)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!dsu__validate_callbacks(callbacks)) {
        return DSU_STATUS_INVALID_ARGS;
    }

    /* Defaults apply when caller does not supply a config or callbacks. */
    dsu_config_init(&cfg_local);
    if (config) {
        cfg_local = *config;
    }
    dsu_callbacks_init(&cbs_local);
    if (callbacks) {
        cbs_local = *callbacks;
    }

    ctx = (dsu_ctx_t *)dsu__malloc((dsu_u32)sizeof(*ctx));
    if (!ctx) {
        return DSU_STATUS_IO_ERROR;
    }
    ctx->config = cfg_local;
    ctx->callbacks = cbs_local;
    ctx->callbacks_user = callbacks_user;
    ctx->audit_log = NULL;
    dsu_platform_iface_init(&ctx->platform_iface);
    ctx->platform_user = NULL;

    st = dsu_log_create(ctx, &ctx->audit_log);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(ctx);
        return st;
    }

    *out_ctx = ctx;
    return DSU_STATUS_SUCCESS;
}

void dsu_ctx_destroy(dsu_ctx_t *ctx) {
    if (!ctx) {
        return;
    }
    if (ctx->audit_log) {
        dsu_log_destroy(ctx, ctx->audit_log);
        ctx->audit_log = NULL;
    }
    dsu__free(ctx);
}

dsu_log_t *dsu_ctx_get_audit_log(dsu_ctx_t *ctx) {
    if (!ctx) {
        return NULL;
    }
    return ctx->audit_log;
}

dsu_status_t dsu_ctx_reset_audit_log(dsu_ctx_t *ctx) {
    if (!ctx) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!ctx->audit_log) {
        return DSU_STATUS_INTERNAL_ERROR;
    }
    return dsu_log_reset(ctx, ctx->audit_log);
}
