#include "dom_shared/manifest_install.h"
#include "dom_shared/json.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/logging.h"

#include <cstdio>
#include <ctime>

namespace dom_shared {

static std::string manifest_path_for_root(const std::string& root)
{
    return os_path_join(root, "dominium_install.json");
}

bool manifest_install_exists(const std::string& root_path)
{
    return os_file_exists(manifest_path_for_root(root_path));
}

static std::string iso_now()
{
    char buf[64];
    std::time_t t = std::time(0);
#ifdef _WIN32
    std::tm tmv;
    gmtime_s(&tmv, &t);
#else
    std::tm tmv;
    gmtime_r(&t, &tmv);
#endif
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tmv);
    return std::string(buf);
}

bool parse_install_manifest(const std::string& root_path, InstallInfo& out_info)
{
    std::string path = manifest_path_for_root(root_path);
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return false;
    }
    std::string content;
    char buf[512];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) {
        content.append(buf, n);
    }
    std::fclose(f);

    JsonValue root;
    if (!json_parse(content, root) || root.type() != JsonValue::Object) {
        return false;
    }
    double schema = root.has("schema_version") ? root["schema_version"].as_number(0.0) : 0.0;
    if ((int)schema != 1) {
        return false;
    }

    InstallInfo info = out_info;
    info.install_id = root.has("install_id") ? root["install_id"].as_string("") : "";
    info.install_type = root.has("install_type") ? root["install_type"].as_string("") : "";
    info.platform = root.has("platform") ? root["platform"].as_string("") : "";
    info.version = root.has("version") ? root["version"].as_string("") : "";
    info.root_path = root.has("root_path") ? root["root_path"].as_string(root_path) : root_path;
    info.created_at = root.has("created_at") ? root["created_at"].as_string("") : "";
    info.created_by = root.has("created_by") ? root["created_by"].as_string("") : "";

    if (info.install_id.empty()) {
        return false;
    }
    if (info.platform.empty()) info.platform = os_get_platform_id();
    if (info.root_path.empty()) info.root_path = root_path;
    out_info = info;
    return true;
}

bool write_install_manifest(const InstallInfo& info_in)
{
    InstallInfo info = info_in;
    if (info.platform.empty()) info.platform = os_get_platform_id();
    if (info.created_at.empty()) info.created_at = iso_now();
    if (info.created_by.empty()) info.created_by = "setup";

    std::string dir = info.root_path;
    if (dir.empty()) return false;
    if (!os_ensure_directory_exists(dir)) {
        log_error("Failed to ensure manifest directory: %s", dir.c_str());
        return false;
    }

    JsonValue root = JsonValue::object();
    root["schema_version"].set_number(1);
    root["install_id"].set_string(info.install_id);
    root["install_type"].set_string(info.install_type);
    root["platform"].set_string(info.platform);
    root["version"].set_string(info.version);
    root["root_path"].set_string(info.root_path);
    root["created_at"].set_string(info.created_at);
    root["created_by"].set_string(info.created_by);

    std::string text = json_stringify(root, true);
    std::string path = manifest_path_for_root(info.root_path);
    FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) {
        log_error("Failed to open manifest for write: %s", path.c_str());
        return false;
    }
    std::fwrite(text.c_str(), 1, text.size(), f);
    std::fclose(f);
    return true;
}

} // namespace dom_shared
