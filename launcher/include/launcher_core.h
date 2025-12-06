// dom_launcher core orchestration (CLI/TUI/GUI share this).
#ifndef DOM_LAUNCHER_CORE_H
#define DOM_LAUNCHER_CORE_H

#include "launcher_discovery.h"
#include "launcher_db.h"
#include "launcher_process.h"

#include <string>
#include <vector>

struct LauncherInstance {
    LauncherProcessHandle process;
    std::string install_id;
    std::string role;
    std::string display_mode;
    std::string exe_path;
};

struct LauncherContext {
    LauncherDb db;
    std::vector<LauncherInstall> discovered_installs;
    std::vector<LauncherInstance> instances;
    std::string launcher_db_path;
};

bool launcher_init_context(LauncherContext &ctx, const std::string &preferred_install_root);
bool launcher_refresh_installs(LauncherContext &ctx);
bool launcher_start_instance(LauncherContext &ctx,
                             const LauncherInstall &install,
                             const std::string &runtime_exe,
                             const std::vector<std::string> &args,
                             const std::string &role,
                             const std::string &display_mode,
                             LauncherInstance &out_instance,
                             std::string &err);
bool launcher_stop_instance(LauncherContext &ctx, const std::string &instance_id);

LauncherInstall *launcher_find_install(LauncherContext &ctx, const std::string &install_id);

#endif /* DOM_LAUNCHER_CORE_H */
