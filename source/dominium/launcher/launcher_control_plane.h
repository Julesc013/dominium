/*
FILE: source/dominium/launcher/launcher_control_plane.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / control_plane
RESPONSIBILITY: Non-interactive control plane commands for dominium-launcher (no UI required).
ALLOWED DEPENDENCIES: `include/dominium/**`, `include/domino/**`, launcher core headers, and C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS headers, UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Stable key=value output ordering; no filesystem enumeration ordering without explicit sorting.
*/
#ifndef DOMINIUM_LAUNCHER_CONTROL_PLANE_H
#define DOMINIUM_LAUNCHER_CONTROL_PLANE_H

#include <cstdio>

extern "C" {
#include "domino/profile.h"
#include "core/include/launcher_core_api.h"
}

namespace dom {

struct ControlPlaneRunResult {
    int handled;   /* 0/1 */
    int exit_code; /* process exit code */

    ControlPlaneRunResult();
};

/* Runs command-style CLI if present:
 * `dominium-launcher <command> [args]`
 *
 * Output: stable, machine-readable key=value lines (no JSON dependency).
 * Audit: appends required reasons to `audit_core` (no silent paths).
 */
ControlPlaneRunResult launcher_control_plane_try_run(int argc,
                                                     char** argv,
                                                     ::launcher_core* audit_core,
                                                     const dom_profile* profile,
                                                     FILE* out,
                                                     FILE* err);

} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CONTROL_PLANE_H */
