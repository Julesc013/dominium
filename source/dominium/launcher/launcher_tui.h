/*
FILE: source/dominium/launcher/launcher_tui.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / tui
RESPONSIBILITY: Internal TUI front-end for dominium-launcher (keyboard-only; deterministic adapter over launcher core ops).
ALLOWED DEPENDENCIES: `include/dominium/**`, `include/domino/**`, launcher core headers, and C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS headers, GUI toolkit headers, and any Plan 8 contract changes.
THREADING MODEL: Single-threaded event loop; no internal synchronization.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: UI does not change core semantics; ordering is explicit and stable.
*/
#ifndef DOMINIUM_LAUNCHER_TUI_H
#define DOMINIUM_LAUNCHER_TUI_H

#include <string>

extern "C" {
#include "domino/profile.h"
#include "core/include/launcher_core_api.h"
}

namespace dom {

/* Runs the launcher TUI.
 * - When `smoke != 0`, performs non-interactive TUI smoke checks and exits.
 */
int launcher_run_tui(const std::string& argv0,
                     const std::string& state_root,
                     ::launcher_core* audit_core,
                     const dom_profile* profile,
                     int smoke);

} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_TUI_H */

