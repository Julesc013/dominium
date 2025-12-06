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
