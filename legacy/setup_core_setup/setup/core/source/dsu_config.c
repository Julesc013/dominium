/*
FILE: source/dominium/setup/core/src/dsu_config.c
MODULE: Dominium Setup
LAYER / SUBSYSTEM: Setup Core configuration helpers
RESPONSIBILITY:
  - Owns initialization of dsu_config_t with ABI/version defaults.
  - Does not validate config or perform IO.
ALLOWED DEPENDENCIES: dsu_config.h, <string.h>.
FORBIDDEN DEPENDENCIES: Platform headers; setup core implementation headers.
THREADING MODEL: Not applicable (pure data initialization).
ERROR MODEL: No error reporting (void function, caller checks for NULL).
DETERMINISM GUARANTEES: Sets deterministic flag by default.
VERSIONING / ABI / DATA FORMAT NOTES: Initializes struct_size and struct_version to DSU_CONFIG_VERSION.
EXTENSION POINTS: None (defaults are centralized here).
*/
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

