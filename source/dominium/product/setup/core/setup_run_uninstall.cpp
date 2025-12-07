#include "dom_setup/dom_setup_config.h"
#include "dom_shared/manifest_install.h"
#include "setup_registration.h"
#include "setup_paths.h"
#include "setup_plugins.h"
#include "dom_shared/logging.h"
#include "dom_shared/os_paths.h"

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#include <io.h>
#else
#include <unistd.h>
#endif

using namespace dom_shared;

static bool remove_tree(const std::string &path)
{
#ifdef _WIN32
    std::string cmd = "cmd /C rmdir /S /Q \"" + path + "\"";
#else
    std::string cmd = "rm -rf \"" + path + "\"";
#endif
    std::system(cmd.c_str());
    return true;
}

int run_uninstall(const SetupConfig &cfg)
{
    dom_shared::InstallInfo info;
    if (!parse_install_manifest(cfg.install_root, info)) {
        log_error("uninstall failed: could not parse manifest");
        return 1;
    }

    remove_shortcuts_for_install(info);
    unregister_install_from_system(info);
    remove_tree(cfg.install_root);

    if (cfg.remove_user_data_on_uninstall) {
        std::string user_root = setup_user_data_root_for_install(info.install_type, cfg.install_root);
        remove_tree(user_root);
    }

    setup_plugins_post_uninstall(info);
    log_info("uninstall completed for %s", cfg.install_root.c_str());
    return 0;
}
