#include "dom_setup_cli.h"
#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"

#include <cstdio>
#include <string>

int dom_setup_cmd_uninstall(const std::string &install_root, bool remove_user_data)
{
    DomInstallManifest manifest;
    std::string err;
    if (!dom_manifest_read(dom_setup_path_join(install_root, "dominium_install.json"), manifest, err)) {
        std::printf("Manifest read failed: %s\n", err.c_str());
        return 1;
    }

    if (!dom_fs_remove_tree(install_root)) {
        std::printf("Failed to remove install root: %s\n", install_root.c_str());
        return 1;
    }

    if (remove_user_data) {
        std::string user_root = dom_setup_user_data_root_for_install(manifest.install_type, install_root);
        if (!user_root.empty()) {
            dom_fs_remove_tree(user_root);
        }
    }

    std::printf("Uninstalled Dominium from %s\n", install_root.c_str());
    return 0;
}
