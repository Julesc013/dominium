/*
FILE: source/dominium/game/core/g_runtime.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/core/g_runtime
RESPONSIBILITY: Implements `g_runtime`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "g_runtime.h"
#include <string.h>

static DmnGameLaunchOptions g_launch_opts = {
    DMN_GAME_MODE_GUI,
    DMN_GAME_SERVER_OFF,
    0
};

void dmn_game_default_options(DmnGameLaunchOptions* out)
{
    if (!out) return;
    *out = g_launch_opts;
}

void dmn_game_set_launch_options(const DmnGameLaunchOptions* opts)
{
    if (!opts) return;
    g_launch_opts = *opts;
}

const DmnGameLaunchOptions* dmn_game_get_launch_options(void)
{
    return &g_launch_opts;
}
