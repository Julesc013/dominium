/*
FILE: source/dominium/setup/core/src/state/dsu_state.c
MODULE: Dominium Setup
PURPOSE: Installed-state stubs for Plan S-1 (format TBD).
*/
#include "../../include/dsu/dsu_state.h"

#include "../util/dsu_util_internal.h"

struct dsu_state {
    dsu_u32 reserved;
};

dsu_status_t dsu_state_load_file(dsu_ctx_t *ctx,
                                const char *path,
                                dsu_state_t **out_state) {
    (void)ctx;
    (void)path;
    if (!out_state) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_state = NULL;
    return DSU_STATUS_UNSUPPORTED_VERSION;
}

dsu_status_t dsu_state_write_file(dsu_ctx_t *ctx,
                                 const dsu_state_t *state,
                                 const char *path) {
    (void)ctx;
    (void)state;
    (void)path;
    return DSU_STATUS_UNSUPPORTED_VERSION;
}

void dsu_state_destroy(dsu_ctx_t *ctx, dsu_state_t *state) {
    (void)ctx;
    dsu__free(state);
}

