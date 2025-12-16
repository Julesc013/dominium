/*
FILE: source/dominium/launcher/cli/dominium_launcher_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/cli/dominium_launcher_cli
RESPONSIBILITY: Implements `dominium_launcher_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/launch_api.h"
#include "dominium_launcher_core.h"
#include "dominium_launcher_view_registry.h"
#include "dominium_launcher_view.h"

#include <stdio.h>
#include <string.h>

int dominium_launcher_run(const char* instance_root_dir)
{
    dominium_launcher_context* ctx = NULL;
    dominium_launcher_view_registry* vreg = NULL;
    const dominium_launcher_view_desc* views = NULL;
    unsigned int view_count = 0;
    const dominium_launcher_view_desc* chosen = NULL;
    unsigned int i;

    (void)instance_root_dir; /* TODO: allow overriding state_root via this */

    if (dominium_launcher_init(&ctx) != 0) {
        return 1;
    }

    vreg = dominium_launcher_get_view_registry(ctx);
    if (dominium_launcher_view_list(vreg, &views, &view_count) != 0) {
        printf("Failed to enumerate launcher views.\n");
        dominium_launcher_shutdown(ctx);
        return 1;
    }

    if (view_count == 0) {
        printf("No launcher views registered.\n");
        dominium_launcher_shutdown(ctx);
        return 0;
    }

    for (i = 0; i < view_count; ++i) {
        if (strcmp(views[i].id, "instances") == 0) {
            chosen = &views[i];
            break;
        }
    }
    if (!chosen) chosen = &views[0];

    if (chosen->render_cli) {
        chosen->render_cli(ctx, (struct dominium_launcher_view*)chosen, NULL);
    } else {
        printf("Selected view '%s' has no CLI renderer.\n", chosen->label);
    }

    dominium_launcher_shutdown(ctx);
    return 0;
}
