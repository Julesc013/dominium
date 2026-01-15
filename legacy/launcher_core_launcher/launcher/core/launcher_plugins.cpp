/*
FILE: source/dominium/launcher/core/launcher_plugins.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/launcher_plugins
RESPONSIBILITY: Implements `launcher_plugins`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "launcher_plugins.h"
#include "launcher_logging.h"
#include "launcher_plugin_api.h"
#include "dom_shared/logging.h"

void launcher_plugins_load(const LauncherContext &ctx)
{
    (void)ctx;
    launcher_log_info("plugin loader stub: no plugins loaded");
}

void launcher_plugins_unload()
{
    launcher_log_info("plugin loader unload");
}

void launcher_plugins_register_builtin()
{
    launcher_log_info("registering builtin tabs/commands (stub)");
}

void launcher_plugins_list()
{
    launcher_log_info("no plugins registered");
}
