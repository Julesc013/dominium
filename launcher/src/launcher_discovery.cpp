#include "launcher_discovery.h"

#include "dom_shared/manifest_install.h"
#include "dom_shared/os_paths.h"
#include "launcher_logging.h"

#include <cstdio>
#include <set>
#include <string>
#include <vector>
#include <sstream>

static bool load_manifest(const std::string &root, LauncherInstall &out)
{
    bool ok = false;
    std::string err;
    InstallInfo manifest = parse_install_manifest(root, ok, err);
    if (!ok) return false;
    out.install_id = manifest.install_id;
    out.install_root = root;
    out.install_type = manifest.install_type;
    out.platform = manifest.platform;
    out.version = manifest.version;
    return true;
}

bool launcher_discover_installs(std::vector<LauncherInstall> &out)
{
    std::set<std::string> seen;
    std::vector<std::string> roots;
    roots.push_back(os_get_default_per_user_install_root());
    roots.push_back(os_get_default_system_install_root());
    roots.push_back(os_get_default_portable_install_root());
    for (size_t i = 0; i < roots.size(); ++i) {
        LauncherInstall inst;
        if (load_manifest(roots[i], inst)) {
            if (seen.find(inst.install_id) == seen.end()) {
                out.push_back(inst);
                seen.insert(inst.install_id);
            }
        }
    }
    std::stringstream ss;
    ss << "Discovered " << out.size() << " installs";
    launcher_log_info(ss.str());
    return true;
}
