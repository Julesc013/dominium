/*
FILE: include/dominium/game/game_app.hpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / game/game_app
RESPONSIBILITY: Defines the public contract for `game_app` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_GAME_APP_HPP
#define DOMINIUM_GAME_APP_HPP

#include "domino/core/types.h"

class GameApp {
public:
/* Purpose: API entry point for `game_app`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    GameApp();
/* Purpose: API entry point for `game_app`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    ~GameApp();

/* Purpose: API entry point for `game_app`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    int run(int argc, char** argv);
/* Purpose: Headless run.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_headless(u32 seed, u32 ticks, u32 width, u32 height);
/* Purpose: Checksum load world.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    int load_world_checksum(const char* path, u32* checksum_out);
/* Purpose: Mode run tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_tui_mode(void);
/* Purpose: Mode run gui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_gui_mode(void);
};

#endif /* DOMINIUM_GAME_APP_HPP */
