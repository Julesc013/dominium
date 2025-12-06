#include "launcher_db.h"

#include "launcher_logging.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <string>

static bool parse_string_field(const std::string &content, const std::string &key, std::string &out, size_t start)
{
    std::string needle = "\"" + key + "\"";
    size_t pos = content.find(needle, start);
    if (pos == std::string::npos) return false;
    pos = content.find(':', pos + needle.size());
    if (pos == std::string::npos) return false;
    ++pos;
    while (pos < content.size() && (content[pos] == ' ' || content[pos] == '\n' || content[pos] == '\t')) ++pos;
    if (pos >= content.size() || content[pos] != '"') return false;
    ++pos;
    std::string value;
    while (pos < content.size() && content[pos] != '"') {
        if (content[pos] == '\\' && pos + 1 < content.size()) ++pos;
        value.push_back(content[pos]);
        ++pos;
    }
    out = value;
    return true;
}

bool launcher_db_load(const std::string &path, LauncherDb &db)
{
    db.schema_version = 1;
    db.path = path;
    db.installs.clear();
    db.profiles.clear();

    FILE *f = std::fopen(path.c_str(), "rb");
    if (!f) {
        launcher_log_info("launcher DB not found, starting clean");
        return true;
    }
    std::string content;
    char buf[512];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) {
        content.append(buf, n);
    }
    std::fclose(f);

    size_t pos = 0;
    while ((pos = content.find("\"install_id\"", pos)) != std::string::npos) {
        size_t obj_start = content.rfind('{', pos);
        size_t obj_end = content.find('}', pos);
        if (obj_start == std::string::npos || obj_end == std::string::npos) break;
        std::string segment = content.substr(obj_start, obj_end - obj_start);
        LauncherInstall inst;
        if (parse_string_field(segment, "install_id", inst.install_id, 0) &&
            parse_string_field(segment, "install_root", inst.install_root, 0)) {
            parse_string_field(segment, "install_type", inst.install_type, 0);
            parse_string_field(segment, "version", inst.version, 0);
            parse_string_field(segment, "platform", inst.platform, 0);
            db.installs.push_back(inst);
        }
        pos = obj_end;
    }

    pos = 0;
    while ((pos = content.find("\"profile_id\"", pos)) != std::string::npos) {
        size_t obj_start = content.rfind('{', pos);
        size_t obj_end = content.find('}', pos);
        if (obj_start == std::string::npos || obj_end == std::string::npos) break;
        std::string segment = content.substr(obj_start, obj_end - obj_start);
        LauncherProfile profile;
        if (parse_string_field(segment, "profile_id", profile.profile_id, 0) &&
            parse_string_field(segment, "name", profile.name, 0)) {
            parse_string_field(segment, "default_install_id", profile.default_install_id, 0);
            db.profiles.push_back(profile);
        }
        pos = obj_end;
    }
    return true;
}

bool launcher_db_save(const LauncherDb &db)
{
    FILE *f = std::fopen(db.path.c_str(), "wb");
    if (!f) return false;
    std::fprintf(f, "{\n");
    std::fprintf(f, "  \"schema_version\": %d,\n", db.schema_version);
    std::fprintf(f, "  \"installs\": [\n");
    for (size_t i = 0; i < db.installs.size(); ++i) {
        const LauncherInstall &inst = db.installs[i];
        std::fprintf(f,
                     "    {\"install_id\":\"%s\",\"install_root\":\"%s\",\"install_type\":\"%s\",\"platform\":\"%s\",\"version\":\"%s\"}%s\n",
                     inst.install_id.c_str(),
                     inst.install_root.c_str(),
                     inst.install_type.c_str(),
                     inst.platform.c_str(),
                     inst.version.c_str(),
                     (i + 1 < db.installs.size()) ? "," : "");
    }
    std::fprintf(f, "  ],\n");
    std::fprintf(f, "  \"profiles\": [\n");
    for (size_t i = 0; i < db.profiles.size(); ++i) {
        const LauncherProfile &p = db.profiles[i];
        std::fprintf(f,
                     "    {\"profile_id\":\"%s\",\"name\":\"%s\",\"default_install_id\":\"%s\"}%s\n",
                     p.profile_id.c_str(),
                     p.name.c_str(),
                     p.default_install_id.c_str(),
                     (i + 1 < db.profiles.size()) ? "," : "");
    }
    std::fprintf(f, "  ]\n");
    std::fprintf(f, "}\n");
    std::fclose(f);
    return true;
}
