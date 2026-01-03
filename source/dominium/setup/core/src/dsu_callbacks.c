/*
FILE: source/dominium/setup/core/src/dsu_callbacks.c
MODULE: Dominium Setup
LAYER / SUBSYSTEM: Setup Core callback helpers
RESPONSIBILITY:
  - Owns initialization of dsu_callbacks_t with ABI/version defaults.
  - Does not implement logging or progress behavior.
ALLOWED DEPENDENCIES: dsu_callbacks.h, <string.h>.
FORBIDDEN DEPENDENCIES: Platform headers; setup core implementation headers.
THREADING MODEL: Not applicable (pure data initialization).
ERROR MODEL: No error reporting (void function, caller checks for NULL).
DETERMINISM GUARANTEES: Callbacks are observational; defaults do not affect determinism.
VERSIONING / ABI / DATA FORMAT NOTES: Initializes struct_size and struct_version to DSU_CALLBACKS_VERSION.
EXTENSION POINTS: None (defaults are centralized here).
*/
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

