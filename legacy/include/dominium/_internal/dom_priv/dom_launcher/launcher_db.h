/*
FILE: include/dominium/_internal/dom_priv/dom_launcher/launcher_db.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_launcher/launcher_db
RESPONSIBILITY: Defines the public contract for `launcher_db` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_DB_H
#define DOM_LAUNCHER_DB_H

#include <string>
#include <vector>
#include <map>
#include "dom_shared/manifest_install.h"

namespace dom_launcher {

struct Profile {
    std::string profile_id;
    std::string name;
    std::string default_install_id;
    std::string default_modset_id;
    std::string preferred_display_mode; // "gui"|"tui"|"cli"|"none"
};

struct ModSetPack {
    std::string id;
    std::string version;
    bool        enabled;
};

struct ModSet {
    std::string modset_id;
    std::string name;
    std::string base_install_id;
    std::vector<ModSetPack> packs;
};

struct ServerEntry {
    std::string server_id;
    std::string address;
    std::string name;
    std::string last_seen;
    std::vector<std::string> tags;
    bool        favorite;
};

struct FriendEntry {
    std::string friend_id;
    std::string display_name;
    bool        online;
    std::string last_presence;
};

struct StatEntry {
    std::string profile_id;
    std::string install_id;
    std::string universe_id;
    long        total_playtime_sec;
};

struct LauncherSettings {
    // Minimal initial fields; will be expanded later
    bool        enable_global_install_discovery;
    bool        auto_update_news;
    int         news_refresh_interval_min;
    bool        auto_update_changes;
    int         changes_refresh_interval_min;
    bool        enable_playtime_stats;
    bool        enable_online_telemetry;

/* Purpose: API entry point for `launcher_db`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    LauncherSettings();
};

struct LauncherDB {
    int schema_version;

    std::vector<dom_shared::InstallInfo> installs;
    std::vector<Profile>                 profiles;
    std::vector<ModSet>                  mod_sets;
    std::vector<ServerEntry>             servers;
    std::vector<FriendEntry>             friends;
    std::vector<StatEntry>               stats;
    std::vector<std::string>             manual_install_paths;

    LauncherSettings                     settings;

    // plugin_id -> (key -> value)
    std::map<std::string, std::map<std::string, std::string> > plugin_data;
};

// Load/save DB from/to user_data_root/db.json
LauncherDB db_load(const std::string& user_data_root);
/* Purpose: Save db.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void       db_save(const std::string& user_data_root, const LauncherDB& db);

} // namespace dom_launcher

#endif
