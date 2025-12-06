#ifndef DOM_LAUNCHER_DB_H
#define DOM_LAUNCHER_DB_H

#include "launcher_context.h"
#include "dom_shared/json.h"

#include <string>
#include <vector>

struct LauncherProfile {
    std::string profile_id;
    std::string name;
    std::string default_install_id;
    std::string default_modset_id;
    std::string preferred_display_mode;
};

struct LauncherModPackRef {
    std::string id;
    std::string version;
};

struct LauncherModSet {
    std::string modset_id;
    std::string name;
    std::vector<LauncherModPackRef> packs;
};

struct LauncherServer {
    std::string server_id;
    std::string address;
    std::string name;
    std::string last_seen;
    std::vector<std::string> tags;
    bool favorite;
};

struct LauncherDb {
    int schema_version;
    std::vector<InstallInfo> installs;
    std::vector<LauncherProfile> profiles;
    std::vector<LauncherModSet> mod_sets;
    std::vector<LauncherServer> servers;
    std::vector<std::string> manual_install_paths;
    JsonValue plugin_data;
};

void db_load(const LauncherContext &ctx);
void db_save(const LauncherContext &ctx);

std::vector<InstallInfo> db_get_installs();
void db_add_or_update_install(const InstallInfo &info);

std::vector<LauncherProfile> db_get_profiles();
void db_add_profile(const LauncherProfile &p);

std::vector<std::string> db_get_manual_paths();
void db_add_manual_path(const std::string &p);

bool db_set_plugin_kv(const std::string &plugin_id, const std::string &key, const std::string &value);
std::string db_get_plugin_kv(const std::string &plugin_id, const std::string &key, const std::string &default_val);

#endif /* DOM_LAUNCHER_DB_H */
