/*
FILE: source/dominium/setup/core/src/dsu_execute.c
MODULE: Dominium Setup
PURPOSE: Execution entry points (DRY_RUN only for Plan S-1).
*/
#include "../include/dsu/dsu_execute.h"
#include "../include/dsu/dsu_log.h"

#include "dsu_ctx_internal.h"
#include "log/dsu_events.h"
#include "util/dsu_util_internal.h"

#include <string.h>

void dsu_execute_options_init(dsu_execute_options_t *opts) {
    if (!opts) {
        return;
    }
    memset(opts, 0, sizeof(*opts));
    opts->struct_size = (dsu_u32)sizeof(*opts);
    opts->struct_version = 1u;
    opts->mode = DSU_EXECUTE_MODE_DRY_RUN;
    opts->log_path = NULL;
}

static const char *dsu__step_kind_name(dsu_plan_step_kind_t kind) {
    switch (kind) {
        case DSU_PLAN_STEP_DECLARE_INSTALL_ROOT: return "DECLARE_INSTALL_ROOT";
        case DSU_PLAN_STEP_INSTALL_COMPONENT: return "INSTALL_COMPONENT";
        case DSU_PLAN_STEP_UPGRADE_COMPONENT: return "UPGRADE_COMPONENT";
        case DSU_PLAN_STEP_REPAIR_COMPONENT: return "REPAIR_COMPONENT";
        case DSU_PLAN_STEP_UNINSTALL_COMPONENT: return "UNINSTALL_COMPONENT";
        case DSU_PLAN_STEP_WRITE_STATE: return "WRITE_STATE";
        case DSU_PLAN_STEP_WRITE_LOG: return "WRITE_LOG";
        default: return "UNKNOWN";
    }
}

static dsu_status_t dsu__emit_step_event(dsu_ctx_t *ctx,
                                        dsu_u32 event_id,
                                        dsu_u8 severity,
                                        dsu_u8 category,
                                        const char *kind_name,
                                        const char *arg) {
    dsu_u32 kind_len;
    dsu_u32 arg_len;
    dsu_u32 total_len;
    char *msg;
    dsu_status_t st;

    if (!ctx || !kind_name) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!arg) {
        arg = "";
    }

    kind_len = dsu__strlen(kind_name);
    arg_len = dsu__strlen(arg);
    total_len = kind_len;
    if (arg_len != 0u) {
        if (total_len > 0xFFFFFFFFu - 2u - arg_len) {
            return DSU_STATUS_INTERNAL_ERROR;
        }
        total_len += 2u + arg_len;
    }
    msg = (char *)dsu__malloc(total_len + 1u);
    if (!msg) {
        return DSU_STATUS_IO_ERROR;
    }
    if (kind_len) {
        memcpy(msg, kind_name, (size_t)kind_len);
    }
    if (arg_len != 0u) {
        msg[kind_len + 0u] = ':';
        msg[kind_len + 1u] = ' ';
        memcpy(msg + kind_len + 2u, arg, (size_t)arg_len);
    }
    msg[total_len] = '\0';

    st = dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      event_id,
                      severity,
                      category,
                      msg);
    dsu__free(msg);
    return st;
}

dsu_status_t dsu_execute_plan(dsu_ctx_t *ctx,
                             const dsu_plan_t *plan,
                             const dsu_execute_options_t *opts) {
    dsu_u32 step_count;
    dsu_u32 i;
    dsu_status_t st;

    if (!ctx || !plan || !opts) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (opts->struct_version != 1u || opts->struct_size < (dsu_u32)sizeof(*opts)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (opts->mode != DSU_EXECUTE_MODE_DRY_RUN) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!opts->log_path || opts->log_path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_DRY_RUN_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_EXECUTE,
                      "dry-run start");
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    step_count = dsu_plan_step_count(plan);
    for (i = 0u; i < step_count; ++i) {
        dsu_plan_step_kind_t kind = dsu_plan_step_kind(plan, i);
        const char *kind_name = dsu__step_kind_name(kind);
        const char *arg = dsu_plan_step_arg(plan, i);

        if (ctx->callbacks.progress) {
            ctx->callbacks.progress(ctx->callbacks_user, i + 1u, step_count, kind_name);
        }

        st = dsu__emit_step_event(ctx,
                                  DSU_EVENT_DRY_RUN_STEP,
                                  (dsu_u8)DSU_LOG_SEVERITY_INFO,
                                  (dsu_u8)DSU_LOG_CATEGORY_EXECUTE,
                                  kind_name,
                                  arg);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
    }

    st = dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_DRY_RUN_COMPLETE,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_EXECUTE,
                      "dry-run complete");
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    /* Export audit log. */
    st = dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_AUDIT_LOG_WRITTEN,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "audit log export");
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    return dsu_log_write_file(ctx, dsu_ctx_get_audit_log(ctx), opts->log_path);
}
