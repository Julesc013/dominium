/*
FILE: source/dominium/game/gui/runtime_display.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/gui/runtime_display
RESPONSIBILITY: Implements `runtime_display`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime_display.h"
#include <cstring>

#ifdef _WIN32
#include <io.h>
#define ISATTY _isatty
#define FILENO _fileno
#else
#include <unistd.h>
#define ISATTY isatty
#define FILENO fileno
#endif

DomDisplayMode parse_display_mode(const std::string &display, bool is_tty)
{
    if (display == "none") return DOM_DISPLAY_NONE;
    if (display == "cli") return DOM_DISPLAY_CLI;
    if (display == "tui") return DOM_DISPLAY_TUI;
    if (display == "gui") return DOM_DISPLAY_GUI;
    /* auto */
    if (is_tty) return DOM_DISPLAY_TUI;
    return DOM_DISPLAY_NONE;
}
