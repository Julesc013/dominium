/*
FILE: source/dominium/launcher/tui/launcher_ui_tui.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/tui/launcher_ui_tui
RESPONSIBILITY: Implements `launcher_ui_tui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher/launcher_ui_tui.h"
#include <cstdio>

namespace dom_launcher {

int launcher_run_tui(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    std::printf("TUI not implemented; use --cli\n");
    return 1;
}

} // namespace dom_launcher
