/*
FILE: source/dominium/setup/core/src/dsu_execute.c
MODULE: Dominium Setup
PURPOSE: Execution entry points (DRY_RUN only for Plan S-1).
*/
#include "../include/dsu/dsu_execute.h"

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

/* dsu_execute_plan is implemented in plan/txn layers (Plan S-1: dry-run only). */

