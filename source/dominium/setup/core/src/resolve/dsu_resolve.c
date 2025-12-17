/*
FILE: source/dominium/setup/core/src/resolve/dsu_resolve.c
MODULE: Dominium Setup
PURPOSE: Resolve stub for Plan S-1 (no dependencies; canonical ordering only).
*/
#include "../../include/dsu/dsu_resolve.h"
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "../log/dsu_events.h"
#include "../util/dsu_util_internal.h"

#include <string.h>

struct dsu_resolved {
    dsu_u32 component_count;
    char **components;
};

static void dsu__resolved_free(dsu_resolved_t *r) {
    dsu_u32 i;
    if (!r) {
        return;
    }
    for (i = 0u; i < r->component_count; ++i) {
        dsu__free(r->components[i]);
    }
    dsu__free(r->components);
    r->components = NULL;
    r->component_count = 0u;
}

dsu_status_t dsu_resolve(dsu_ctx_t *ctx,
                        const dsu_manifest_t *manifest,
                        dsu_resolved_t **out_resolved) {
    dsu_resolved_t *r;
    dsu_u32 count;
    dsu_u32 i;
    char **items;

    if (!ctx || !manifest || !out_resolved) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_resolved = NULL;

    count = dsu_manifest_component_count(manifest);
    items = (char **)dsu__malloc(count * (dsu_u32)sizeof(*items));
    if (!items && count != 0u) {
        return DSU_STATUS_IO_ERROR;
    }
    for (i = 0u; i < count; ++i) {
        const char *id = dsu_manifest_component_id(manifest, i);
        items[i] = dsu__strdup(id ? id : "");
        if (!items[i]) {
            dsu_u32 j;
            for (j = 0u; j < i; ++j) {
                dsu__free(items[j]);
            }
            dsu__free(items);
            return DSU_STATUS_IO_ERROR;
        }
    }

    r = (dsu_resolved_t *)dsu__malloc((dsu_u32)sizeof(*r));
    if (!r) {
        for (i = 0u; i < count; ++i) {
            dsu__free(items[i]);
        }
        dsu__free(items);
        return DSU_STATUS_IO_ERROR;
    }
    memset(r, 0, sizeof(*r));
    r->component_count = count;
    r->components = items;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_RESOLVE_COMPLETE,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_RESOLVE,
                      "resolve complete");

    *out_resolved = r;
    return DSU_STATUS_SUCCESS;
}

void dsu_resolved_destroy(dsu_ctx_t *ctx, dsu_resolved_t *resolved) {
    (void)ctx;
    if (!resolved) {
        return;
    }
    dsu__resolved_free(resolved);
    dsu__free(resolved);
}

dsu_u32 dsu_resolved_component_count(const dsu_resolved_t *resolved) {
    if (!resolved) {
        return 0u;
    }
    return resolved->component_count;
}

const char *dsu_resolved_component_id(const dsu_resolved_t *resolved, dsu_u32 index) {
    if (!resolved || index >= resolved->component_count) {
        return NULL;
    }
    return resolved->components[index];
}

