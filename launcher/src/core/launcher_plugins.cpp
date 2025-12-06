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
