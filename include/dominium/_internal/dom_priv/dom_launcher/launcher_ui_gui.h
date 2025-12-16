/*
FILE: include/dominium/_internal/dom_priv/dom_launcher/launcher_ui_gui.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_launcher/launcher_ui_gui
RESPONSIBILITY: Defines internal contract for `launcher_ui_gui` entry points; not a stable public API; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal header; no ABI stability guarantees.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_UI_GUI_H
#define DOM_LAUNCHER_UI_GUI_H

namespace dom_launcher {

/* Purpose: Run the launcher GUI entry point.
 *
 * Parameters:
 * - `argc`/`argv`: Host arguments; interpretation is implementation-defined.
 *
 * Returns:
 * - 0 when the GUI was started and completed successfully.
 * - Non-zero to signal the caller should fall back to another UI (e.g., CLI/TUI).
 */
int launcher_run_gui(int argc, char** argv);

} // namespace dom_launcher

#endif
