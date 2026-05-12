/*
FILE: include/dominium/_internal/dom_priv/dom_launcher/launcher_discovery.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_launcher/launcher_discovery
RESPONSIBILITY: Defines the public contract for `launcher_discovery` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_DISCOVERY_H
#define DOM_LAUNCHER_DISCOVERY_H

#include <vector>
#include "dom_contracts/dom_shared/manifest_install.h"
#include "launcher_state.h"

namespace dom_launcher {

/* Purpose: Installs discover.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::vector<dom_shared::InstallInfo> discover_installs(const LauncherState& state);

// Helper to merge discovered installs into state.db.installs sensibly.
void merge_discovered_installs(LauncherState& state,
                               const std::vector<dom_shared::InstallInfo>& discovered);

} // namespace dom_launcher

#endif
