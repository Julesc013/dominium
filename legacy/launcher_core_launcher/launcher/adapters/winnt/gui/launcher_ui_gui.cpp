/*
FILE: source/dominium/launcher/gui/launcher_ui_gui.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/gui/launcher_ui_gui
RESPONSIBILITY: Implements `launcher_ui_gui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher/launcher_ui_gui.h"
#include <cstdio>

namespace dom_launcher {

int launcher_run_gui(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    std::printf("GUI not implemented; falling back to CLI\n");
    return 1;
}

} // namespace dom_launcher
