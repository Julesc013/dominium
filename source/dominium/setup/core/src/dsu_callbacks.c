/*
FILE: source/dominium/setup/core/src/dsu_callbacks.c
MODULE: Dominium Setup
PURPOSE: Setup Core callback helpers.
*/
#include "../include/dsu/dsu_callbacks.h"

#include <string.h>

void dsu_callbacks_init(dsu_callbacks_t *cbs) {
    if (!cbs) {
        return;
    }
    memset(cbs, 0, sizeof(*cbs));
    cbs->struct_size = (dsu_u32)sizeof(*cbs);
    cbs->struct_version = DSU_CALLBACKS_VERSION;
    cbs->log = NULL;
    cbs->progress = NULL;
}

