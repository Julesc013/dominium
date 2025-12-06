#include "dom_setup_config.h"
#include "dom_shared/manifest_install.h"
#include "setup_registration.h"
#include "setup_plugins.h"
#include "dom_shared/logging.h"
#include "dom_shared/os_paths.h"

#include <cstdio>

int run_repair(const SetupConfig &cfg)
{
    bool ok = false;
    std::string err;
    InstallInfo info = parse_install_manifest(cfg.install_root, ok, err);
    if (!ok) {
        log_error("repair failed: " + err);
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
    log_info("repair completed for " + cfg.install_root);
    return 0;
}
