#include "dom_setup_cli.h"
#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"

#include <cstdio>
#include <string>
#include <vector>

struct InstallRecord {
    DomInstallManifest manifest;
    std::string root;
};

static bool try_load_manifest(const std::string &root, InstallRecord &out)
{
    std::string manifest_path = dom_setup_path_join(root, "dominium_install.json");
    if (!dom_fs_path_exists(manifest_path)) return false;
    std::string err;
    if (!dom_manifest_read(manifest_path, out.manifest, err)) {
        return false;
    }
    out.root = root;
    return true;
}

static void scan_root(const std::string &root, std::vector<InstallRecord> &out)
{
    InstallRecord rec;
    if (try_load_manifest(root, rec)) {
        out.push_back(rec);
    }
    std::vector<std::string> entries = dom_fs_list_dir(root);
    for (size_t i = 0; i < entries.size(); ++i) {
        std::string child = dom_setup_path_join(root, entries[i]);
        if (dom_fs_is_dir(child)) {
            if (try_load_manifest(child, rec)) {
                out.push_back(rec);
            }
        }
    }
}

int dom_setup_cmd_list()
{
    std::vector<InstallRecord> installs;
    scan_root(dom_setup_default_install_root_per_user(), installs);
    scan_root(dom_setup_default_install_root_system(), installs);
    scan_root(dom_setup_get_cwd(), installs);

    for (size_t i = 0; i < installs.size(); ++i) {
        const InstallRecord &r = installs[i];
        std::printf("%s | %s | %s | %s\n",
                    r.manifest.install_id.c_str(),
                    r.root.c_str(),
                    r.manifest.install_type.c_str(),
                    r.manifest.version.c_str());
    }
    if (installs.empty()) {
        std::printf("No installs discovered.\n");
    }
    return 0;
}

int dom_setup_cmd_info(const std::string &install_root)
{
    DomInstallManifest manifest;
    std::string err;
    if (!dom_manifest_read(dom_setup_path_join(install_root, "dominium_install.json"), manifest, err)) {
        std::printf("Manifest read failed: %s\n", err.c_str());
        return 1;
    }
    std::printf("install_root: %s\n", install_root.c_str());
    std::printf("install_id: %s\n", manifest.install_id.c_str());
    std::printf("install_type: %s\n", manifest.install_type.c_str());
    std::printf("platform: %s\n", manifest.platform.c_str());
    std::printf("version: %s\n", manifest.version.c_str());
    std::printf("created_at: %s\n", manifest.created_at.c_str());
    std::printf("created_by: %s\n", manifest.created_by.c_str());
    return 0;
}
