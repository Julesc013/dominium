/*
FILE: include/dominium/_internal/dom_priv/dom_launcher/launcher_context.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_launcher/launcher_context
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

#include <string>
#include "dom_shared/manifest_install.h"

namespace dom_launcher {

struct LauncherContext {
    dom_shared::InstallInfo self_install;   // may be synthetic if no manifest
    std::string user_data_root;            // where launcher db/logs live
    bool        portable_mode;             // true if install_type == "portable"
    std::string session_id;                // per-launch UUID
};

LauncherContext init_launcher_context();

const LauncherContext& get_launcher_context();

} // namespace dom_launcher

#endif
