// Launcher DB persistence (db.json).
#ifndef DOM_LAUNCHER_DB_H
#define DOM_LAUNCHER_DB_H

#include "launcher_discovery.h"

#include <string>
#include <vector>

struct LauncherProfile {
    std::string profile_id;
    std::string name;
    std::string default_install_id;
};

struct LauncherDb {
    int schema_version;
    std::string path;
    std::vector<LauncherInstall> installs;
    std::vector<LauncherProfile> profiles;
};

bool launcher_db_load(const std::string &path, LauncherDb &db);
bool launcher_db_save(const LauncherDb &db);

#endif /* DOM_LAUNCHER_DB_H */
