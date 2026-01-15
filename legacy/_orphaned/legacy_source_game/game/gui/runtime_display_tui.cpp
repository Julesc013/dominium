/*
FILE: source/dominium/game/gui/runtime_display_tui.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/gui/runtime_display_tui
RESPONSIBILITY: Implements `runtime_display_tui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime_display.h"
#include "runtime_app.h"

#include <cstdio>

int run_game_tui(const RuntimeConfig &cfg)
{
    std::printf("dom_main (TUI stub) role=%s universe=%s display=tui\n",
                cfg.role.c_str(),
                cfg.universe_path.c_str());
    return 0;
}
