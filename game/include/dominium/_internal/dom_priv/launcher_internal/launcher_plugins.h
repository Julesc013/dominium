/*
FILE: include/dominium/_internal/dom_priv/launcher_internal/launcher_plugins.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/launcher_internal/launcher_plugins
RESPONSIBILITY: Defines the public contract for `launcher_plugins` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_PLUGINS_H
#define DOM_LAUNCHER_PLUGINS_H

#include "launcher_context.h"
#include "launcher_process.h"
#include "launcher_db.h"

/* Purpose: Load plugins.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void launcher_plugins_load(const LauncherContext &ctx);
/* Purpose: Unload launcher plugins.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void launcher_plugins_unload();
/* Purpose: Register builtin.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void launcher_plugins_register_builtin();
/* Purpose: List launcher plugins.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void launcher_plugins_list();

#endif /* DOM_LAUNCHER_PLUGINS_H */
