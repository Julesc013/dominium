/*
FILE: include/dominium/launcher/launcher_app.hpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / launcher/launcher_app
RESPONSIBILITY: Defines the public contract for `launcher_app` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCHER_APP_HPP
#define DOMINIUM_LAUNCHER_APP_HPP

#include "domino/core/types.h"

class LauncherApp {
public:
/* Purpose: API entry point for `launcher_app`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    LauncherApp();
/* Purpose: API entry point for `launcher_app`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    ~LauncherApp();

/* Purpose: API entry point for `launcher_app`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int run(int argc, char** argv);
/* Purpose: Products run list.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_list_products();
/* Purpose: Game run run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_run_game(u32 seed, u32 ticks, const char* instance_id);
/* Purpose: Tool run run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_run_tool(const char* tool_id);
/* Purpose: Info run manifest.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_manifest_info();
/* Purpose: Tui run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_tui();
/* Purpose: Gui run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int run_gui();
};

#endif /* DOMINIUM_LAUNCHER_APP_HPP */
