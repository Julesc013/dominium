#include "dom_setup_config.h"
#include "dom_shared/manifest_install.h"
#include "setup_registration.h"
#include "setup_plugins.h"
#include "dom_shared/logging.h"
#include "dom_shared/os_paths.h"

#include <cstdio>

using namespace dom_shared;

int run_repair(const SetupConfig &cfg)
{
    dom_shared::InstallInfo info;
    if (!parse_install_manifest(cfg.install_root, info)) {
        log_error("repair failed: could not parse manifest");
        return 1;
    }
    /* Stub validation: ensure manifest exists and recreate shortcuts/registration */
    if (cfg.register_system) {
        register_install_with_system(info);
    }
    if (cfg.create_shortcuts) {
        create_shortcuts_for_install(info);
    }
    setup_plugins_post_repair(info);
    log_info("repair completed for %s", cfg.install_root.c_str());
    return 0;
}
