/*
FILE: source/dominium/launcher/core/launcher_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/launcher_state
RESPONSIBILITY: Implements `launcher_state`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher/launcher_state.h"
#include "dom_launcher/launcher_context.h"
#include "dom_launcher/launcher_db.h"

namespace dom_launcher {

static LauncherState g_state;
static bool g_state_inited = false;

LauncherState& get_state()
{
    return g_state;
}

void state_initialize()
{
    LauncherContext ctx = init_launcher_context();
    g_state.ctx = ctx;
    g_state.db = db_load(ctx.user_data_root);
    g_state.installs.clear();
    g_state.news = 0;
    g_state.changes = 0;
    g_state.mods = 0;
    g_state.instances_state = 0;
    g_state.settings_state = 0;
    g_state_inited = true;
}

void state_save()
{
    if (!g_state_inited) {
        state_initialize();
    }
    db_save(g_state.ctx.user_data_root, g_state.db);
}

} // namespace dom_launcher
