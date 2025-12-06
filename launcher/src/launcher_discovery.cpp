#include "launcher_discovery.h"

#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"
#include "launcher_logging.h"

#include <cstdio>
#include <set>
#include <string>
#include <vector>
#include <sstream>

static bool load_manifest(const std::string &root, LauncherInstall &out)
{
    DomInstallManifest manifest;
    std::string err;
    if (!dom_manifest_read(dom_setup_path_join(root, "dominium_install.json"), manifest, err)) {
        return false;
    }
    out.install_id = manifest.install_id;
    out.install_root = root;
    out.install_type = manifest.install_type;
    out.platform = manifest.platform;
    out.version = manifest.version;
    return true;
}

static void scan_root(const std::string &root, std::vector<LauncherInstall> &out, std::set<std::string> &seen)
{
    LauncherInstall inst;
    if (load_manifest(root, inst)) {
        if (seen.find(inst.install_id) == seen.end()) {
            out.push_back(inst);
            seen.insert(inst.install_id);
        }
    }
    std::vector<std::string> entries = dom_fs_list_dir(root);
    for (size_t i = 0; i < entries.size(); ++i) {
        std::string child = dom_setup_path_join(root, entries[i]);
        if (!dom_fs_is_dir(child)) continue;
        if (load_manifest(child, inst)) {
            if (seen.find(inst.install_id) == seen.end()) {
                out.push_back(inst);
                seen.insert(inst.install_id);
            }
        }
    }
}

bool launcher_discover_installs(std::vector<LauncherInstall> &out)
{
    std::set<std::string> seen;
    scan_root(dom_setup_default_install_root_per_user(), out, seen);
    scan_root(dom_setup_default_install_root_system(), out, seen);
    scan_root(dom_setup_get_cwd(), out, seen);

    // Read index (best effort) written by dom_setup install.
    std::string index_path = dom_setup_install_index_path();
    if (dom_fs_path_exists(index_path)) {
        FILE *f = std::fopen(index_path.c_str(), "rb");
        if (f) {
            char line[1024];
            while (std::fgets(line, sizeof(line), f)) {
                std::string s(line);
                size_t p1 = s.find('|');
                size_t p2 = s.find('|', p1 == std::string::npos ? 0 : p1 + 1);
                size_t p3 = s.find('|', p2 == std::string::npos ? 0 : p2 + 1);
                if (p1 != std::string::npos && p2 != std::string::npos) {
                    std::string install_id = s.substr(0, p1);
                    std::string root = s.substr(p1 + 1, p2 - p1 - 1);
                    LauncherInstall inst;
                    inst.install_id = install_id;
                    inst.install_root = root;
                    if (p2 != std::string::npos && p3 != std::string::npos) {
                        inst.install_type = s.substr(p2 + 1, p3 - p2 - 1);
                        inst.version = s.substr(p3 + 1);
                        if (!inst.version.empty() && inst.version[inst.version.size() - 1] == '\n') {
                            inst.version.erase(inst.version.size() - 1);
                        }
                    }
                    if (seen.find(inst.install_id) == seen.end()) {
                        if (inst.install_type.empty()) inst.install_type = "unknown";
                        inst.platform = dom_manifest_platform_tag();
                        out.push_back(inst);
                        seen.insert(inst.install_id);
                    }
                }
            }
            std::fclose(f);
        }
    }

    std::stringstream ss;
    ss << "Discovered " << out.size() << " installs";
    launcher_log_info(ss.str());
    return true;
}
