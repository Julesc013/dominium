#include "launcher_discovery.h"
#include "launcher_logging.h"
#include "launcher_db.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/manifest_install.h"

#include <set>
#include <sstream>

static bool load_manifest(const std::string &root, InstallInfo &out)
{
    bool ok = false;
    std::string err;
    out = parse_install_manifest(root, ok, err);
    return ok;
}

InstallInfo *find_install_by_id(std::vector<InstallInfo> &installs, const std::string &id)
{
    for (size_t i = 0; i < installs.size(); ++i) {
        if (installs[i].install_id == id) return &installs[i];
    }
    return 0;
}

InstallInfo *find_install_by_root(std::vector<InstallInfo> &installs, const std::string &root)
{
    for (size_t i = 0; i < installs.size(); ++i) {
        if (installs[i].root_path == root) return &installs[i];
    }
    return 0;
}

std::vector<InstallInfo> discover_installs(const LauncherContext &ctx)
{
    std::vector<InstallInfo> out;
    std::set<std::string> seen_ids;
    if (!ctx.self_install.install_id.empty()) {
        out.push_back(ctx.self_install);
        seen_ids.insert(ctx.self_install.install_id);
    }
    std::vector<std::string> roots = os_get_default_install_roots();
    std::vector<std::string> manual = db_get_manual_paths();
    roots.insert(roots.end(), manual.begin(), manual.end());
    for (size_t i = 0; i < roots.size(); ++i) {
        InstallInfo ii;
        if (load_manifest(roots[i], ii)) {
            if (seen_ids.find(ii.install_id) == seen_ids.end()) {
                out.push_back(ii);
                seen_ids.insert(ii.install_id);
            }
        }
    }
    std::stringstream ss;
    ss << "discovered installs: " << out.size();
    launcher_log_info(ss.str());
    return out;
}
