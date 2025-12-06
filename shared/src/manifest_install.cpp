#include "dom_shared/manifest_install.h"
#include "dom_shared/json.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/logging.h"

#include <cstdio>
#include <ctime>

static std::string manifest_path_for_root(const std::string &root)
{
    return os_path_join(root, "dominium_install.json");
}

bool manifest_exists(const std::string &root_path)
{
    std::string p = manifest_path_for_root(root_path);
    FILE *f = std::fopen(p.c_str(), "rb");
    if (f) {
        std::fclose(f);
        return true;
    }
    return false;
}

InstallInfo parse_install_manifest(const std::string &root_path, bool &ok, std::string &err)
{
    InstallInfo info;
    ok = false;
    err.clear();
    std::string path = manifest_path_for_root(root_path);
    FILE *f = std::fopen(path.c_str(), "rb");
    if (!f) {
        err = "manifest not found";
        return info;
    }
    std::string content;
    char buf[512];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) {
        content.append(buf, n);
    }
    std::fclose(f);
    JsonValue root;
    if (!json_parse(content, root) || root.kind != JsonValue::JSON_OBJECT) {
        err = "invalid json";
        return info;
    }
    info.root_path = root_path;
    if (root.object_values.find("install_id") != root.object_values.end())
        info.install_id = root.object_values["install_id"].string_value;
    if (root.object_values.find("install_type") != root.object_values.end())
        info.install_type = root.object_values["install_type"].string_value;
    if (root.object_values.find("platform") != root.object_values.end())
        info.platform = root.object_values["platform"].string_value;
    if (root.object_values.find("version") != root.object_values.end())
        info.version = root.object_values["version"].string_value;
    if (root.object_values.find("created_at") != root.object_values.end())
        info.created_at = root.object_values["created_at"].string_value;
    if (root.object_values.find("created_by") != root.object_values.end())
        info.created_by = root.object_values["created_by"].string_value;
    if (info.install_id.empty()) { err = "missing install_id"; return info; }
    ok = true;
    return info;
}

static std::string iso_now()
{
    char buf[64];
    std::time_t t = std::time(0);
#ifdef _WIN32
    std::tm tmv;
    gmtime_s(&tmv, &t);
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tmv);
#else
    std::tm tmv;
    gmtime_r(&t, &tmv);
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tmv);
#endif
    return std::string(buf);
}

void write_install_manifest(const InstallInfo &info_in, bool &ok, std::string &err)
{
    InstallInfo info = info_in;
    ok = false;
    err.clear();
    std::string path = manifest_path_for_root(info.root_path);

    JsonValue root = JsonValue::make_object();
    root.object_values["schema_version"] = JsonValue::make_number(1);
    root.object_values["install_id"] = JsonValue::make_string(info.install_id);
    root.object_values["install_type"] = JsonValue::make_string(info.install_type);
    root.object_values["platform"] = JsonValue::make_string(info.platform.empty() ? os_get_platform_id() : info.platform);
    root.object_values["version"] = JsonValue::make_string(info.version);
    root.object_values["created_at"] = JsonValue::make_string(info.created_at.empty() ? iso_now() : info.created_at);
    root.object_values["created_by"] = JsonValue::make_string(info.created_by.empty() ? "setup" : info.created_by);

    std::string text = json_stringify(root, 0);
    FILE *f = std::fopen(path.c_str(), "wb");
    if (!f) {
        err = "failed to open manifest for write";
        return;
    }
    std::fwrite(text.c_str(), 1, text.size(), f);
    std::fclose(f);
    ok = true;
    log_info("Wrote manifest at " + path);
}
