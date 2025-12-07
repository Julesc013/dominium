#include "dom_launcher/launcher_db.h"
#include "dom_shared/json.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/uuid.h"

#include <cstdio>

namespace dom_launcher {

LauncherSettings::LauncherSettings()
{
    enable_global_install_discovery = true;
    auto_update_news = true;
    news_refresh_interval_min = 60;
    auto_update_changes = true;
    changes_refresh_interval_min = 60;
    enable_playtime_stats = true;
    enable_online_telemetry = false;
}

static dom_shared::JsonValue install_to_json(const dom_shared::InstallInfo& i)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    obj["install_id"].set_string(i.install_id);
    obj["install_type"].set_string(i.install_type);
    obj["platform"].set_string(i.platform);
    obj["version"].set_string(i.version);
    obj["root_path"].set_string(i.root_path);
    obj["created_at"].set_string(i.created_at);
    obj["created_by"].set_string(i.created_by);
    return obj;
}

static bool json_to_install(const dom_shared::JsonValue& v, dom_shared::InstallInfo& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return false;
    dom_shared::InstallInfo i;
    i.install_id = v.has("install_id") ? v["install_id"].as_string("") : "";
    i.install_type = v.has("install_type") ? v["install_type"].as_string("") : "";
    i.platform = v.has("platform") ? v["platform"].as_string("") : "";
    i.version = v.has("version") ? v["version"].as_string("") : "";
    i.root_path = v.has("root_path") ? v["root_path"].as_string("") : "";
    i.created_at = v.has("created_at") ? v["created_at"].as_string("") : "";
    i.created_by = v.has("created_by") ? v["created_by"].as_string("") : "";
    if (i.install_id.empty()) return false;
    out = i;
    return true;
}

static dom_shared::JsonValue profile_to_json(const Profile& p)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    obj["profile_id"].set_string(p.profile_id);
    obj["name"].set_string(p.name);
    obj["default_install_id"].set_string(p.default_install_id);
    obj["default_modset_id"].set_string(p.default_modset_id);
    obj["preferred_display_mode"].set_string(p.preferred_display_mode);
    return obj;
}

static bool json_to_profile(const dom_shared::JsonValue& v, Profile& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return false;
    Profile p;
    p.profile_id = v.has("profile_id") ? v["profile_id"].as_string("") : "";
    p.name = v.has("name") ? v["name"].as_string("") : "";
    p.default_install_id = v.has("default_install_id") ? v["default_install_id"].as_string("") : "";
    p.default_modset_id = v.has("default_modset_id") ? v["default_modset_id"].as_string("") : "";
    p.preferred_display_mode = v.has("preferred_display_mode") ? v["preferred_display_mode"].as_string("") : "";
    out = p;
    return true;
}

static dom_shared::JsonValue modset_to_json(const ModSet& m)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    obj["modset_id"].set_string(m.modset_id);
    obj["name"].set_string(m.name);
    obj["base_install_id"].set_string(m.base_install_id);
    dom_shared::JsonValue packs = dom_shared::JsonValue::array();
    for (size_t i = 0; i < m.packs.size(); ++i) {
        dom_shared::JsonValue p = dom_shared::JsonValue::object();
        p["id"].set_string(m.packs[i].id);
        p["version"].set_string(m.packs[i].version);
        p["enabled"].set_bool(m.packs[i].enabled);
        packs.push_back(p);
    }
    obj["packs"] = packs;
    return obj;
}

static bool json_to_modset(const dom_shared::JsonValue& v, ModSet& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return false;
    ModSet m;
    m.modset_id = v.has("modset_id") ? v["modset_id"].as_string("") : "";
    m.name = v.has("name") ? v["name"].as_string("") : "";
    m.base_install_id = v.has("base_install_id") ? v["base_install_id"].as_string("") : "";
    if (v.has("packs") && v["packs"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& packs = v["packs"].array_items();
        for (size_t i = 0; i < packs.size(); ++i) {
            const dom_shared::JsonValue& pv = packs[i];
            if (pv.type() != dom_shared::JsonValue::Object) continue;
            ModSetPack pack;
            pack.id = pv.has("id") ? pv["id"].as_string("") : "";
            pack.version = pv.has("version") ? pv["version"].as_string("") : "";
            pack.enabled = pv.has("enabled") ? pv["enabled"].as_bool(true) : true;
            m.packs.push_back(pack);
        }
    }
    out = m;
    return true;
}

static dom_shared::JsonValue server_to_json(const ServerEntry& s)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    obj["server_id"].set_string(s.server_id);
    obj["address"].set_string(s.address);
    obj["name"].set_string(s.name);
    obj["last_seen"].set_string(s.last_seen);
    obj["favorite"].set_bool(s.favorite);
    dom_shared::JsonValue tags = dom_shared::JsonValue::array();
    for (size_t i = 0; i < s.tags.size(); ++i) {
        dom_shared::JsonValue t;
        t.set_string(s.tags[i]);
        tags.push_back(t);
    }
    obj["tags"] = tags;
    return obj;
}

static bool json_to_server(const dom_shared::JsonValue& v, ServerEntry& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return false;
    ServerEntry s;
    s.server_id = v.has("server_id") ? v["server_id"].as_string("") : "";
    s.address = v.has("address") ? v["address"].as_string("") : "";
    s.name = v.has("name") ? v["name"].as_string("") : "";
    s.last_seen = v.has("last_seen") ? v["last_seen"].as_string("") : "";
    s.favorite = v.has("favorite") ? v["favorite"].as_bool(false) : false;
    if (v.has("tags") && v["tags"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& tags = v["tags"].array_items();
        for (size_t i = 0; i < tags.size(); ++i) {
            s.tags.push_back(tags[i].as_string(""));
        }
    }
    out = s;
    return true;
}

static dom_shared::JsonValue friend_to_json(const FriendEntry& f)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    obj["friend_id"].set_string(f.friend_id);
    obj["display_name"].set_string(f.display_name);
    obj["online"].set_bool(f.online);
    obj["last_presence"].set_string(f.last_presence);
    return obj;
}

static bool json_to_friend(const dom_shared::JsonValue& v, FriendEntry& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return false;
    FriendEntry f;
    f.friend_id = v.has("friend_id") ? v["friend_id"].as_string("") : "";
    f.display_name = v.has("display_name") ? v["display_name"].as_string("") : "";
    f.online = v.has("online") ? v["online"].as_bool(false) : false;
    f.last_presence = v.has("last_presence") ? v["last_presence"].as_string("") : "";
    out = f;
    return true;
}

static dom_shared::JsonValue stat_to_json(const StatEntry& s)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    obj["profile_id"].set_string(s.profile_id);
    obj["install_id"].set_string(s.install_id);
    obj["universe_id"].set_string(s.universe_id);
    obj["total_playtime_sec"].set_number((double)s.total_playtime_sec);
    return obj;
}

static bool json_to_stat(const dom_shared::JsonValue& v, StatEntry& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return false;
    StatEntry s;
    s.profile_id = v.has("profile_id") ? v["profile_id"].as_string("") : "";
    s.install_id = v.has("install_id") ? v["install_id"].as_string("") : "";
    s.universe_id = v.has("universe_id") ? v["universe_id"].as_string("") : "";
    s.total_playtime_sec = v.has("total_playtime_sec") ? (long)v["total_playtime_sec"].as_number(0.0) : 0;
    out = s;
    return true;
}

static dom_shared::JsonValue settings_to_json(const LauncherSettings& s)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    obj["enable_global_install_discovery"].set_bool(s.enable_global_install_discovery);
    obj["auto_update_news"].set_bool(s.auto_update_news);
    obj["news_refresh_interval_min"].set_number((double)s.news_refresh_interval_min);
    obj["auto_update_changes"].set_bool(s.auto_update_changes);
    obj["changes_refresh_interval_min"].set_number((double)s.changes_refresh_interval_min);
    obj["enable_playtime_stats"].set_bool(s.enable_playtime_stats);
    obj["enable_online_telemetry"].set_bool(s.enable_online_telemetry);
    return obj;
}

static void json_to_settings(const dom_shared::JsonValue& v, LauncherSettings& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return;
    if (v.has("enable_global_install_discovery")) out.enable_global_install_discovery = v["enable_global_install_discovery"].as_bool(out.enable_global_install_discovery);
    if (v.has("auto_update_news")) out.auto_update_news = v["auto_update_news"].as_bool(out.auto_update_news);
    if (v.has("news_refresh_interval_min")) out.news_refresh_interval_min = (int)v["news_refresh_interval_min"].as_number((double)out.news_refresh_interval_min);
    if (v.has("auto_update_changes")) out.auto_update_changes = v["auto_update_changes"].as_bool(out.auto_update_changes);
    if (v.has("changes_refresh_interval_min")) out.changes_refresh_interval_min = (int)v["changes_refresh_interval_min"].as_number((double)out.changes_refresh_interval_min);
    if (v.has("enable_playtime_stats")) out.enable_playtime_stats = v["enable_playtime_stats"].as_bool(out.enable_playtime_stats);
    if (v.has("enable_online_telemetry")) out.enable_online_telemetry = v["enable_online_telemetry"].as_bool(out.enable_online_telemetry);
}

static dom_shared::JsonValue plugin_data_to_json(const std::map<std::string, std::map<std::string, std::string> >& pd)
{
    dom_shared::JsonValue obj = dom_shared::JsonValue::object();
    for (std::map<std::string, std::map<std::string, std::string> >::const_iterator it = pd.begin(); it != pd.end(); ++it) {
        dom_shared::JsonValue plug = dom_shared::JsonValue::object();
        const std::map<std::string, std::string>& entries = it->second;
        for (std::map<std::string, std::string>::const_iterator kv = entries.begin(); kv != entries.end(); ++kv) {
            plug[kv->first].set_string(kv->second);
        }
        obj[it->first] = plug;
    }
    return obj;
}

static void json_to_plugin_data(const dom_shared::JsonValue& v, std::map<std::string, std::map<std::string, std::string> >& out)
{
    if (v.type() != dom_shared::JsonValue::Object) return;
    const std::map<std::string, dom_shared::JsonValue>& plugins = v.object_items();
    for (std::map<std::string, dom_shared::JsonValue>::const_iterator it = plugins.begin(); it != plugins.end(); ++it) {
        std::map<std::string, std::string> kv_map;
        if (it->second.type() == dom_shared::JsonValue::Object) {
            const std::map<std::string, dom_shared::JsonValue>& kvs = it->second.object_items();
            for (std::map<std::string, dom_shared::JsonValue>::const_iterator kv = kvs.begin(); kv != kvs.end(); ++kv) {
                kv_map[kv->first] = kv->second.as_string("");
            }
        }
        out[it->first] = kv_map;
    }
}

static std::string db_path(const std::string& root)
{
    return dom_shared::os_path_join(root, "db.json");
}

static LauncherDB default_db()
{
    LauncherDB db;
    db.schema_version = 1;
    db.settings = LauncherSettings();
    Profile p;
    p.profile_id = dom_shared::generate_uuid();
    p.name = "Default";
    p.default_install_id = "";
    p.default_modset_id = "";
    p.preferred_display_mode = "gui";
    db.profiles.push_back(p);
    return db;
}

LauncherDB db_load(const std::string& user_data_root)
{
    LauncherDB db = default_db();
    std::string path = db_path(user_data_root);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return db;
    }

    std::string content;
    char buf[512];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) content.append(buf, n);
    std::fclose(f);

    dom_shared::JsonValue root;
    if (!dom_shared::json_parse(content, root) || root.type() != dom_shared::JsonValue::Object) {
        return db;
    }

    db.installs.clear();
    db.profiles.clear();
    db.mod_sets.clear();
    db.servers.clear();
    db.friends.clear();
    db.stats.clear();
    db.manual_install_paths.clear();
    db.plugin_data.clear();
    db.settings = LauncherSettings();

    db.schema_version = root.has("schema_version") ? (int)root["schema_version"].as_number(1) : 1;
    if (root.has("installs") && root["installs"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& arr = root["installs"].array_items();
        for (size_t i = 0; i < arr.size(); ++i) {
            dom_shared::InstallInfo info;
            if (json_to_install(arr[i], info)) db.installs.push_back(info);
        }
    }
    if (root.has("profiles") && root["profiles"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& arr = root["profiles"].array_items();
        for (size_t i = 0; i < arr.size(); ++i) {
            Profile p;
            if (json_to_profile(arr[i], p)) db.profiles.push_back(p);
        }
    }
    if (root.has("mod_sets") && root["mod_sets"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& arr = root["mod_sets"].array_items();
        for (size_t i = 0; i < arr.size(); ++i) {
            ModSet m;
            if (json_to_modset(arr[i], m)) db.mod_sets.push_back(m);
        }
    }
    if (root.has("servers") && root["servers"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& arr = root["servers"].array_items();
        for (size_t i = 0; i < arr.size(); ++i) {
            ServerEntry s;
            if (json_to_server(arr[i], s)) db.servers.push_back(s);
        }
    }
    if (root.has("friends") && root["friends"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& arr = root["friends"].array_items();
        for (size_t i = 0; i < arr.size(); ++i) {
            FriendEntry fentry;
            if (json_to_friend(arr[i], fentry)) db.friends.push_back(fentry);
        }
    }
    if (root.has("stats") && root["stats"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& arr = root["stats"].array_items();
        for (size_t i = 0; i < arr.size(); ++i) {
            StatEntry st;
            if (json_to_stat(arr[i], st)) db.stats.push_back(st);
        }
    }
    if (root.has("manual_install_paths") && root["manual_install_paths"].type() == dom_shared::JsonValue::Array) {
        const std::vector<dom_shared::JsonValue>& arr = root["manual_install_paths"].array_items();
        for (size_t i = 0; i < arr.size(); ++i) {
            db.manual_install_paths.push_back(arr[i].as_string(""));
        }
    }
    if (root.has("settings")) {
        json_to_settings(root["settings"], db.settings);
    }
    if (root.has("plugin_data")) {
        json_to_plugin_data(root["plugin_data"], db.plugin_data);
    }

    if (db.profiles.empty()) {
        db.profiles.push_back(default_db().profiles[0]);
    }
    return db;
}

void db_save(const std::string& user_data_root, const LauncherDB& db)
{
    dom_shared::JsonValue root = dom_shared::JsonValue::object();
    root["schema_version"].set_number((double)db.schema_version);

    dom_shared::JsonValue installs = dom_shared::JsonValue::array();
    for (size_t i = 0; i < db.installs.size(); ++i) installs.push_back(install_to_json(db.installs[i]));
    root["installs"] = installs;

    dom_shared::JsonValue profiles = dom_shared::JsonValue::array();
    for (size_t i = 0; i < db.profiles.size(); ++i) profiles.push_back(profile_to_json(db.profiles[i]));
    root["profiles"] = profiles;

    dom_shared::JsonValue modsets = dom_shared::JsonValue::array();
    for (size_t i = 0; i < db.mod_sets.size(); ++i) modsets.push_back(modset_to_json(db.mod_sets[i]));
    root["mod_sets"] = modsets;

    dom_shared::JsonValue servers = dom_shared::JsonValue::array();
    for (size_t i = 0; i < db.servers.size(); ++i) servers.push_back(server_to_json(db.servers[i]));
    root["servers"] = servers;

    dom_shared::JsonValue friends_arr = dom_shared::JsonValue::array();
    for (size_t i = 0; i < db.friends.size(); ++i) friends_arr.push_back(friend_to_json(db.friends[i]));
    root["friends"] = friends_arr;

    dom_shared::JsonValue stats = dom_shared::JsonValue::array();
    for (size_t i = 0; i < db.stats.size(); ++i) stats.push_back(stat_to_json(db.stats[i]));
    root["stats"] = stats;

    dom_shared::JsonValue manual = dom_shared::JsonValue::array();
    for (size_t i = 0; i < db.manual_install_paths.size(); ++i) {
        dom_shared::JsonValue v;
        v.set_string(db.manual_install_paths[i]);
        manual.push_back(v);
    }
    root["manual_install_paths"] = manual;

    root["settings"] = settings_to_json(db.settings);
    root["plugin_data"] = plugin_data_to_json(db.plugin_data);

    std::string text = dom_shared::json_stringify(root, true);
    std::string path = db_path(user_data_root);
    dom_shared::os_ensure_directory_exists(user_data_root);
    FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) {
        return;
    }
    std::fwrite(text.c_str(), 1, text.size(), f);
    std::fclose(f);
}

} // namespace dom_launcher
