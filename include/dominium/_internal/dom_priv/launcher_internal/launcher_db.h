/*
FILE: include/dominium/_internal/dom_priv/launcher_internal/launcher_db.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/launcher_internal/launcher_db
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
    std::vector<dom_shared::InstallInfo> installs;
    std::vector<LauncherProfile> profiles;
    std::vector<LauncherModSet> mod_sets;
    std::vector<LauncherServer> servers;
    std::vector<std::string> manual_install_paths;
    dom_shared::JsonValue plugin_data;
};

/* Purpose: Load db.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void db_load(const LauncherContext &ctx);
/* Purpose: Save db.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void db_save(const LauncherContext &ctx);

/* Purpose: Installs db get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::vector<dom_shared::InstallInfo> db_get_installs();
/* Purpose: Install db add or update.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void db_add_or_update_install(const dom_shared::InstallInfo &info);

/* Purpose: Profiles db get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::vector<LauncherProfile> db_get_profiles();
/* Purpose: Profile db add.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void db_add_profile(const LauncherProfile &p);

/* Purpose: Paths db get manual.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::vector<std::string> db_get_manual_paths();
/* Purpose: Path db add manual.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void db_add_manual_path(const std::string &p);

/* Purpose: Kv db set plugin.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool db_set_plugin_kv(const std::string &plugin_id, const std::string &key, const std::string &value);
/* Purpose: Kv db get plugin.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
std::string db_get_plugin_kv(const std::string &plugin_id, const std::string &key, const std::string &default_val);

#endif /* DOM_LAUNCHER_DB_H */
