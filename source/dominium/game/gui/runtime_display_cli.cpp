/*
FILE: source/dominium/game/gui/runtime_display_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/gui/runtime_display_cli
RESPONSIBILITY: Implements `runtime_display_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

int run_game_cli(const RuntimeConfig &cfg)
{
    std::printf("dom_main (CLI) role=%s universe=%s display=cli session=%s instance=%s\n",
                cfg.role.c_str(),
                cfg.universe_path.c_str(),
                cfg.launcher_session_id.c_str(),
                cfg.launcher_instance_id.c_str());
    return 0;
}
