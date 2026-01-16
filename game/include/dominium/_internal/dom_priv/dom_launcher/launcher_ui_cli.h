/*
FILE: include/dominium/_internal/dom_priv/dom_launcher/launcher_ui_cli.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_launcher/launcher_ui_cli
RESPONSIBILITY: Defines internal contract for `launcher_ui_cli` entry points; not a stable public API; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal header; no ABI stability guarantees.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_UI_CLI_H
#define DOM_LAUNCHER_UI_CLI_H

namespace dom_launcher {

/* Purpose: Run a simple interactive launcher CLI (development stub).
 *
 * Parameters:
 * - `argc`/`argv`: Reserved for parity with other launcher entry points; currently unused by the stub.
 *
 * Returns:
 * - 0 on normal exit.
 */
int launcher_run_cli(int argc, char** argv);

} // namespace dom_launcher

#endif
