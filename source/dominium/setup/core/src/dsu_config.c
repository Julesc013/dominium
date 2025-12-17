/*
FILE: source/dominium/setup/core/src/dsu_config.c
MODULE: Dominium Setup
PURPOSE: Setup Core configuration helpers.
*/
#include "../include/dsu/dsu_config.h"

#include <string.h>

void dsu_config_init(dsu_config_t *cfg) {
    if (!cfg) {
        return;
    }
    memset(cfg, 0, sizeof(*cfg));
    cfg->struct_size = (dsu_u32)sizeof(*cfg);
    cfg->struct_version = DSU_CONFIG_VERSION;
    cfg->flags = DSU_CONFIG_FLAG_DETERMINISTIC;
    cfg->max_file_bytes = 0u;
}

