#include "dom_setup_config.h"
#include "dom_shared/manifest_install.h"
#include "dom_shared/logging.h"
#include "dom_shared/os_paths.h"

#include <cstdio>
#include <vector>

using namespace dom_shared;

static void discover_in_root(const std::string &root, std::vector<InstallInfo> &out)
{
    if (manifest_install_exists(root)) {
        InstallInfo info;
        if (parse_install_manifest(root, info)) {
            out.push_back(info);
        }
    }
}

int run_list(const SetupConfig &cfg)
{
    (void)cfg;
    std::vector<InstallInfo> installs;
    discover_in_root(os_get_default_per_user_install_root(), installs);
    discover_in_root(os_get_default_system_install_root(), installs);
    discover_in_root(os_get_default_portable_install_root(), installs);
    for (size_t i = 0; i < installs.size(); ++i) {
        std::printf("%s | %s | %s | %s\n",
                    installs[i].root_path.c_str(),
                    installs[i].install_type.c_str(),
                    installs[i].platform.c_str(),
                    installs[i].install_id.c_str());
    }
    if (installs.empty()) {
        std::printf("No installs found\n");
    }
    return 0;
}

int run_info(const SetupConfig &cfg)
{
    InstallInfo info;
    if (!parse_install_manifest(cfg.install_root, info)) {
        log_error("info failed: could not parse manifest");
        return 1;
    }
    std::printf("{\"install_id\":\"%s\",\"install_type\":\"%s\",\"platform\":\"%s\",\"version\":\"%s\",\"root_path\":\"%s\"}\n",
                info.install_id.c_str(),
                info.install_type.c_str(),
                info.platform.c_str(),
                info.version.c_str(),
                info.root_path.c_str());
    return 0;
}
