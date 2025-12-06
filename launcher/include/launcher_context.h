#ifndef DOM_LAUNCHER_CONTEXT_H
#define DOM_LAUNCHER_CONTEXT_H

#include "dom_shared/manifest_install.h"

#include <string>

struct LauncherContext {
    InstallInfo self_install;
    std::string user_data_root;
    bool portable_mode;
    std::string session_id;
};

LauncherContext init_launcher_context();
const LauncherContext &get_launcher_context();

#endif /* DOM_LAUNCHER_CONTEXT_H */
