/*
FILE: source/dominium/launcher/model/dominium_launcher_model.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/model/dominium_launcher_model
RESPONSIBILITY: Implements `dominium_launcher_model`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium_launcher_model.h"

#include <string.h>

int dominium_launcher_build_views(dominium_launcher_context* ctx,
                                  dominium_launcher_instance_view* out,
                                  unsigned int max_count,
                                  unsigned int* out_count)
{
    domino_instance_desc instances[DOMINIUM_LAUNCHER_MAX_INSTANCES];
    unsigned int total = 0;
    unsigned int i;

    if (out_count) *out_count = 0;
    if (!ctx || !out) return -1;

    dominium_launcher_list_instances(ctx, instances, DOMINIUM_LAUNCHER_MAX_INSTANCES, &total);
    if (out_count) *out_count = total;
    for (i = 0; i < total && i < max_count; ++i) {
        domino_resolve_error err;
        err.message[0] = '\0';
        memset(&out[i], 0, sizeof(out[i]));
        strncpy(out[i].id, instances[i].id, sizeof(out[i].id) - 1);
        strncpy(out[i].label, instances[i].label, sizeof(out[i].label) - 1);
        strncpy(out[i].product_id, instances[i].product_id, sizeof(out[i].product_id) - 1);
        out[i].product_version = instances[i].product_version;
        out[i].mod_count = instances[i].mod_count;
        out[i].pack_count = instances[i].pack_count;
        out[i].compatible = (dominium_launcher_resolve_instance(ctx, &instances[i], &err) == 0) ? 1 : 0;
    }
    return 0;
}
