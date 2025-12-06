// Install discovery helpers (manifest-driven).
#ifndef DOM_LAUNCHER_DISCOVERY_H
#define DOM_LAUNCHER_DISCOVERY_H

#include <string>
#include <vector>

struct LauncherInstall {
    std::string install_id;
    std::string install_root;
    std::string install_type;
    std::string platform;
    std::string version;
};

bool launcher_discover_installs(std::vector<LauncherInstall> &out);

#endif /* DOM_LAUNCHER_DISCOVERY_H */
