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
    LauncherApp();
    ~LauncherApp();

    int run(int argc, char** argv);
    int run_list_products();
    int run_run_game(u32 seed, u32 ticks, const char* instance_id);
    int run_run_tool(const char* tool_id);
    int run_manifest_info();
    int run_tui();
    int run_gui();
};

#endif /* DOMINIUM_LAUNCHER_APP_HPP */
