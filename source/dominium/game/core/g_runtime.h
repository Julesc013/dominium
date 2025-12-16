/*
FILE: source/dominium/game/core/g_runtime.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/core/g_runtime
RESPONSIBILITY: Defines internal contract for `g_runtime`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DMN_GAME_RUNTIME_H
#define DMN_GAME_RUNTIME_H

typedef enum DmnGameMode_ {
    DMN_GAME_MODE_GUI,
    DMN_GAME_MODE_TUI,
    DMN_GAME_MODE_HEADLESS
} DmnGameMode;

typedef enum DmnGameServerMode_ {
    DMN_GAME_SERVER_OFF,
    DMN_GAME_SERVER_LISTEN,
    DMN_GAME_SERVER_DEDICATED
} DmnGameServerMode;

typedef struct DmnGameLaunchOptions_ {
    DmnGameMode       mode;
    DmnGameServerMode server_mode;
    int               demo_mode;
} DmnGameLaunchOptions;

void dmn_game_default_options(DmnGameLaunchOptions* out);
void dmn_game_set_launch_options(const DmnGameLaunchOptions* opts);
const DmnGameLaunchOptions* dmn_game_get_launch_options(void);

#endif /* DMN_GAME_RUNTIME_H */
