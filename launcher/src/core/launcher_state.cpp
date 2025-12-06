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
