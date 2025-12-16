/*
FILE: include/dominium/_internal/dom_priv/launcher_internal/launcher_discovery.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/launcher_internal/launcher_discovery
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

#include "launcher_context.h"

#include <string>
#include <vector>

std::vector<InstallInfo> discover_installs(const LauncherContext &ctx);
InstallInfo *find_install_by_id(std::vector<InstallInfo> &installs, const std::string &id);
InstallInfo *find_install_by_root(std::vector<InstallInfo> &installs, const std::string &root);

#endif /* DOM_LAUNCHER_DISCOVERY_H */
