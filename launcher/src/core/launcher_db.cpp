#include "launcher_db.h"
#include "launcher_logging.h"
#include "dom_shared/os_paths.h"

#include <cstdio>

static LauncherDb g_db;
static std::string g_db_path;
static bool g_loaded = false;

static void ensure_db_path(const LauncherContext &ctx)
{
    g_db_path = os_path_join(ctx.user_data_root, "db.json");
}

static void reset_defaults()
{
    g_db.schema_version = 1;
    g_db.installs.clear();
    g_db.profiles.clear();
    g_db.mod_sets.clear();
    g_db.servers.clear();
    g_db.manual_install_paths.clear();
    g_db.plugin_data = JsonValue::make_object();
}

static JsonValue install_to_json(const InstallInfo &i)
{
    JsonValue obj = JsonValue::make_object();
    obj.object_values["install_id"] = JsonValue::make_string(i.install_id);
    obj.object_values["install_type"] = JsonValue::make_string(i.install_type);
    obj.object_values["platform"] = JsonValue::make_string(i.platform);
    obj.object_values["version"] = JsonValue::make_string(i.version);
    obj.object_values["root_path"] = JsonValue::make_string(i.root_path);
    obj.object_values["created_at"] = JsonValue::make_string(i.created_at);
    obj.object_values["created_by"] = JsonValue::make_string(i.created_by);
    return obj;
}

static bool json_to_install(const JsonValue &v, InstallInfo &out)
{
    if (v.kind != JsonValue::JSON_OBJECT) return false;
    out.install_id = v.object_values.find("install_id") != v.object_values.end() ? v.object_values.find("install_id")->second.string_value : "";
    out.install_type = v.object_values.find("install_type") != v.object_values.end() ? v.object_values.find("install_type")->second.string_value : "";
    out.platform = v.object_values.find("platform") != v.object_values.end() ? v.object_values.find("platform")->second.string_value : "";
    out.version = v.object_values.find("version") != v.object_values.end() ? v.object_values.find("version")->second.string_value : "";
    out.root_path = v.object_values.find("root_path") != v.object_values.end() ? v.object_values.find("root_path")->second.string_value : "";
    out.created_at = v.object_values.find("created_at") != v.object_values.end() ? v.object_values.find("created_at")->second.string_value : "";
    out.created_by = v.object_values.find("created_by") != v.object_values.end() ? v.object_values.find("created_by")->second.string_value : "";
    return !out.install_id.empty();
}

static JsonValue profile_to_json(const LauncherProfile &p)
{
    JsonValue obj = JsonValue::make_object();
    obj.object_values["profile_id"] = JsonValue::make_string(p.profile_id);
    obj.object_values["name"] = JsonValue::make_string(p.name);
    obj.object_values["default_install_id"] = JsonValue::make_string(p.default_install_id);
    obj.object_values["default_modset_id"] = JsonValue::make_string(p.default_modset_id);
    obj.object_values["preferred_display_mode"] = JsonValue::make_string(p.preferred_display_mode);
    return obj;
}

static JsonValue modset_to_json(const LauncherModSet &m)
{
    JsonValue obj = JsonValue::make_object();
    obj.object_values["modset_id"] = JsonValue::make_string(m.modset_id);
    obj.object_values["name"] = JsonValue::make_string(m.name);
    JsonValue arr = JsonValue::make_array();
    for (size_t i = 0; i < m.packs.size(); ++i) {
        JsonValue p = JsonValue::make_object();
        p.object_values["id"] = JsonValue::make_string(m.packs[i].id);
        p.object_values["version"] = JsonValue::make_string(m.packs[i].version);
        arr.array_values.push_back(p);
    }
    obj.object_values["packs"] = arr;
    return obj;
}

static JsonValue server_to_json(const LauncherServer &s)
{
    JsonValue obj = JsonValue::make_object();
    obj.object_values["server_id"] = JsonValue::make_string(s.server_id);
    obj.object_values["address"] = JsonValue::make_string(s.address);
    obj.object_values["name"] = JsonValue::make_string(s.name);
    obj.object_values["last_seen"] = JsonValue::make_string(s.last_seen);
    JsonValue tags = JsonValue::make_array();
    for (size_t i = 0; i < s.tags.size(); ++i) tags.array_values.push_back(JsonValue::make_string(s.tags[i]));
    obj.object_values["tags"] = tags;
    obj.object_values["favorite"] = JsonValue::make_bool(s.favorite);
    return obj;
}

void db_load(const LauncherContext &ctx)
{
    ensure_db_path(ctx);
    reset_defaults();
    FILE *f = std::fopen(g_db_path.c_str(), "rb");
    if (!f) {
        g_loaded = true;
        return;
    }
    std::string content;
    char buf[512];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) content.append(buf, n);
    std::fclose(f);
    JsonValue root;
    if (!json_parse(content, root) || root.kind != JsonValue::JSON_OBJECT) {
        g_loaded = true;
        return;
    }
    JsonValue installs = root.object_values["installs"];
    if (installs.kind == JsonValue::JSON_ARRAY) {
        for (size_t i = 0; i < installs.array_values.size(); ++i) {
            InstallInfo ii;
            if (json_to_install(installs.array_values[i], ii)) g_db.installs.push_back(ii);
        }
    }
    JsonValue profiles = root.object_values["profiles"];
    if (profiles.kind == JsonValue::JSON_ARRAY) {
        for (size_t i = 0; i < profiles.array_values.size(); ++i) {
            const JsonValue &p = profiles.array_values[i];
            if (p.kind != JsonValue::JSON_OBJECT) continue;
            LauncherProfile prof;
            prof.profile_id = p.object_values["profile_id"].string_value;
            prof.name = p.object_values["name"].string_value;
            prof.default_install_id = p.object_values["default_install_id"].string_value;
            prof.default_modset_id = p.object_values["default_modset_id"].string_value;
            prof.preferred_display_mode = p.object_values["preferred_display_mode"].string_value;
            g_db.profiles.push_back(prof);
        }
    }
    JsonValue modsets = root.object_values["mod_sets"];
    if (modsets.kind == JsonValue::JSON_ARRAY) {
        for (size_t i = 0; i < modsets.array_values.size(); ++i) {
            const JsonValue &m = modsets.array_values[i];
            if (m.kind != JsonValue::JSON_OBJECT) continue;
            LauncherModSet ms;
            ms.modset_id = m.object_values["modset_id"].string_value;
            ms.name = m.object_values["name"].string_value;
            const JsonValue &packs = m.object_values["packs"];
            if (packs.kind == JsonValue::JSON_ARRAY) {
                for (size_t j = 0; j < packs.array_values.size(); ++j) {
                    LauncherModPackRef ref;
                    const JsonValue &pv = packs.array_values[j];
                    if (pv.kind != JsonValue::JSON_OBJECT) continue;
                    ref.id = pv.object_values.find("id") != pv.object_values.end() ? pv.object_values.find("id")->second.string_value : "";
                    ref.version = pv.object_values.find("version") != pv.object_values.end() ? pv.object_values.find("version")->second.string_value : "";
                    ms.packs.push_back(ref);
                }
            }
            g_db.mod_sets.push_back(ms);
        }
    }
    JsonValue servers = root.object_values["servers"];
    if (servers.kind == JsonValue::JSON_ARRAY) {
        for (size_t i = 0; i < servers.array_values.size(); ++i) {
            const JsonValue &sv = servers.array_values[i];
            if (sv.kind != JsonValue::JSON_OBJECT) continue;
            LauncherServer s;
            s.server_id = sv.object_values["server_id"].string_value;
            s.address = sv.object_values["address"].string_value;
            s.name = sv.object_values["name"].string_value;
            s.last_seen = sv.object_values["last_seen"].string_value;
            s.favorite = sv.object_values.find("favorite") != sv.object_values.end() ? sv.object_values.find("favorite")->second.bool_value : false;
            const JsonValue &tags = sv.object_values["tags"];
            if (tags.kind == JsonValue::JSON_ARRAY) {
                for (size_t j = 0; j < tags.array_values.size(); ++j) {
                    s.tags.push_back(tags.array_values[j].string_value);
                }
            }
            g_db.servers.push_back(s);
        }
    }
    JsonValue manual = root.object_values["manual_install_paths"];
    if (manual.kind == JsonValue::JSON_ARRAY) {
        for (size_t i = 0; i < manual.array_values.size(); ++i) {
            g_db.manual_install_paths.push_back(manual.array_values[i].string_value);
        }
    }
    if (root.object_values.find("plugin_data") != root.object_values.end()) {
        g_db.plugin_data = root.object_values.find("plugin_data")->second;
    }
    g_loaded = true;
}

void db_save(const LauncherContext &ctx)
{
    if (!g_loaded) return;
    ensure_db_path(ctx);
    JsonValue root = JsonValue::make_object();
    root.object_values["schema_version"] = JsonValue::make_number(g_db.schema_version);
    JsonValue installs = JsonValue::make_array();
    for (size_t i = 0; i < g_db.installs.size(); ++i) {
        installs.array_values.push_back(install_to_json(g_db.installs[i]));
    }
    root.object_values["installs"] = installs;

    JsonValue profiles = JsonValue::make_array();
    for (size_t i = 0; i < g_db.profiles.size(); ++i) profiles.array_values.push_back(profile_to_json(g_db.profiles[i]));
    root.object_values["profiles"] = profiles;

    JsonValue modsets = JsonValue::make_array();
    for (size_t i = 0; i < g_db.mod_sets.size(); ++i) modsets.array_values.push_back(modset_to_json(g_db.mod_sets[i]));
    root.object_values["mod_sets"] = modsets;

    JsonValue servers = JsonValue::make_array();
    for (size_t i = 0; i < g_db.servers.size(); ++i) servers.array_values.push_back(server_to_json(g_db.servers[i]));
    root.object_values["servers"] = servers;

    JsonValue manual = JsonValue::make_array();
    for (size_t i = 0; i < g_db.manual_install_paths.size(); ++i) manual.array_values.push_back(JsonValue::make_string(g_db.manual_install_paths[i]));
    root.object_values["manual_install_paths"] = manual;

    root.object_values["plugin_data"] = g_db.plugin_data.kind == JsonValue::JSON_NULL ? JsonValue::make_object() : g_db.plugin_data;

    std::string text = json_stringify(root, 0);
    FILE *f = std::fopen(g_db_path.c_str(), "wb");
    if (!f) return;
    std::fwrite(text.c_str(), 1, text.size(), f);
    std::fclose(f);
}

std::vector<InstallInfo> db_get_installs() { return g_db.installs; }

void db_add_or_update_install(const InstallInfo &info)
{
    for (size_t i = 0; i < g_db.installs.size(); ++i) {
        if (g_db.installs[i].install_id == info.install_id || g_db.installs[i].root_path == info.root_path) {
            g_db.installs[i] = info;
            return;
        }
    }
    g_db.installs.push_back(info);
}

std::vector<LauncherProfile> db_get_profiles() { return g_db.profiles; }

void db_add_profile(const LauncherProfile &p)
{
    g_db.profiles.push_back(p);
}

std::vector<std::string> db_get_manual_paths() { return g_db.manual_install_paths; }

void db_add_manual_path(const std::string &p)
{
    g_db.manual_install_paths.push_back(p);
}

bool db_set_plugin_kv(const std::string &plugin_id, const std::string &key, const std::string &value)
{
    if (g_db.plugin_data.kind != JsonValue::JSON_OBJECT) g_db.plugin_data = JsonValue::make_object();
    JsonValue &pd = g_db.plugin_data;
    if (pd.object_values.find(plugin_id) == pd.object_values.end()) {
        pd.object_values[plugin_id] = JsonValue::make_object();
    }
    pd.object_values[plugin_id].object_values[key] = JsonValue::make_string(value);
    return true;
}

std::string db_get_plugin_kv(const std::string &plugin_id, const std::string &key, const std::string &default_val)
{
    if (g_db.plugin_data.kind != JsonValue::JSON_OBJECT) return default_val;
    std::map<std::string, JsonValue>::iterator it = g_db.plugin_data.object_values.find(plugin_id);
    if (it == g_db.plugin_data.object_values.end()) return default_val;
    std::map<std::string, JsonValue>::iterator jt = it->second.object_values.find(key);
    if (jt == it->second.object_values.end()) return default_val;
    return jt->second.string_value;
}
