/*
FILE: source/dominium/game/cli/dominium_game_cli_main.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/cli/dominium_game_cli_main
RESPONSIBILITY: Implements `dominium_game_cli_main`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "../dom_game_cli.h"

int main(int argc, char** argv)
{
    return dom_game_cli_dispatch(argc, argv);
}
