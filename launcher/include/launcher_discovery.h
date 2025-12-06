#ifndef DOM_LAUNCHER_DISCOVERY_H
#define DOM_LAUNCHER_DISCOVERY_H

#include "launcher_context.h"

#include <string>
#include <vector>

std::vector<InstallInfo> discover_installs(const LauncherContext &ctx);
InstallInfo *find_install_by_id(std::vector<InstallInfo> &installs, const std::string &id);
InstallInfo *find_install_by_root(std::vector<InstallInfo> &installs, const std::string &root);

#endif /* DOM_LAUNCHER_DISCOVERY_H */
