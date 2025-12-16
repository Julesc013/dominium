/*
FILE: source/dominium/game/gui/runtime_app.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/gui/runtime_app
RESPONSIBILITY: Implements `runtime_app`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
// dom_main runtime application entry helpers.
#ifndef DOM_MAIN_RUNTIME_APP_H
#define DOM_MAIN_RUNTIME_APP_H

#include <string>

struct RuntimeConfig {
    std::string role;          /* client | server | tool */
    std::string display;       /* none | cli | tui | gui | auto */
    std::string universe_path;
    std::string launcher_session_id;
    std::string launcher_instance_id;
    std::string launcher_integration; /* auto | off */
};

int runtime_print_version();
int runtime_print_capabilities();
int runtime_run(const RuntimeConfig &cfg);

#endif /* DOM_MAIN_RUNTIME_APP_H */
