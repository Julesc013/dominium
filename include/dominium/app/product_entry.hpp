/*
FILE: include/dominium/app/product_entry.hpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / app/product_entry
RESPONSIBILITY: Defines the public contract for `product_entry` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_APP_PRODUCT_ENTRY_HPP
#define DOMINIUM_APP_PRODUCT_ENTRY_HPP

extern "C" {

struct d_app_params; /* forward from Domino C header */

/* Purpose: Cli dom launcher run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_launcher_run_cli(const d_app_params* p);
/* Purpose: Tui dom launcher run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_launcher_run_tui(const d_app_params* p);
/* Purpose: Gui dom launcher run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_launcher_run_gui(const d_app_params* p);

/* Purpose: Cli dom game run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_game_run_cli(const d_app_params* p);
/* Purpose: Tui dom game run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_game_run_tui(const d_app_params* p);
/* Purpose: Gui dom game run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_game_run_gui(const d_app_params* p);
/* Purpose: Headless dom game run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_game_run_headless(const d_app_params* p);

/* Purpose: Cli dom setup run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_setup_run_cli(const d_app_params* p);
/* Purpose: Tui dom setup run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_setup_run_tui(const d_app_params* p);
/* Purpose: Gui dom setup run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_setup_run_gui(const d_app_params* p);

/* Purpose: Cli dom tools run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_tools_run_cli(const d_app_params* p);
/* Purpose: Tui dom tools run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_tools_run_tui(const d_app_params* p);
/* Purpose: Gui dom tools run.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_tools_run_gui(const d_app_params* p);

} /* extern \"C\" */

#endif
