/*
FILE: source/dominium/launcher/main_launcher.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/main_launcher
RESPONSIBILITY: Implements `main_launcher`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/system/dsys.h"
#include "domino/app/startup.h"

int main(int argc, char** argv) {
    d_app_params p;
    p.argc = argc;
    p.argv = argv;
    p.has_terminal = dsys_running_in_terminal();
    p.mode = d_app_parse_mode(argc, argv);

    return d_app_run_launcher(&p);
}
