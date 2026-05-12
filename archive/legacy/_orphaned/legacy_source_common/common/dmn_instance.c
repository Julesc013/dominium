/*
FILE: source/dominium/common/dmn_instance.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dmn_instance
RESPONSIBILITY: Implements `dmn_instance`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/instance.h"
#include <stdlib.h>
#include <string.h>

int dmn_instance_load(const char* instance_id, DmnInstance* out)
{
    if (!instance_id || !out) return -1;
    memset(out, 0, sizeof(*out));
    strncpy(out->instance_id, instance_id, sizeof(out->instance_id) - 1);
    strncpy(out->label, instance_id, sizeof(out->label) - 1);
    out->flags.demo_mode = 0;
    return 0;
}

int dmn_instance_save(const DmnInstance* inst)
{
    (void)inst;
    return -1;
}

int dmn_instance_list(DmnInstanceList* out)
{
    if (out) {
        out->instances = NULL;
        out->count = 0;
    }
    return 0;
}

void dmn_instance_list_free(DmnInstanceList* list)
{
    if (!list) return;
    if (list->instances) {
        free(list->instances);
        list->instances = NULL;
    }
    list->count = 0;
}
