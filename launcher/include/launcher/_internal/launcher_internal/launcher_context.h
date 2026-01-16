/*
FILE: include/dominium/_internal/dom_priv/launcher_internal/launcher_context.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/launcher_internal/launcher_context
RESPONSIBILITY: Defines the public contract for `launcher_context` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_CONTEXT_H
#define DOM_LAUNCHER_CONTEXT_H

#include "dom_contracts/dom_shared/manifest_install.h"

#include <string>

struct LauncherContext {
    dom_shared::InstallInfo self_install;
    std::string user_data_root;
    bool portable_mode;
    std::string session_id;
};

/* Purpose: Context init launcher.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
LauncherContext init_launcher_context();
/* Purpose: Context get launcher.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
const LauncherContext &get_launcher_context();

#endif /* DOM_LAUNCHER_CONTEXT_H */
