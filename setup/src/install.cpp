#include "dom_setup_cli.h"
#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"
#include "dom_setup_fs.h"

#include <cstdio>
#include <ctime>
#include <string>
#include <vector>

static std::string iso_now()
{
    char buf[64];
    std::time_t t = std::time(0);
#ifdef _WIN32
    struct tm tmv;
    gmtime_s(&tmv, &t);
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tmv);
#else
    struct tm tmv;
    gmtime_r(&t, &tmv);
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tmv);
#endif
    return std::string(buf);
}

static bool write_placeholder(const std::string &install_root)
{
    std::string path = dom_setup_path_join(install_root, "README_INSTALL.txt");
    FILE *f = std::fopen(path.c_str(), "wb");
    if (!f) return false;
    std::fprintf(f, "Dominium install placeholder\n");
    std::fprintf(f, "This install was created by dom_setup. Populate bin/ with built artifacts.\n");
    std::fclose(f);
    return true;
}

static void ensure_minimal_layout(const std::string &root)
{
    dom_fs_make_dirs(dom_setup_path_join(root, "bin"));
    dom_fs_make_dirs(dom_setup_path_join(root, "mods"));
    dom_fs_make_dirs(dom_setup_path_join(root, "data"));
    dom_fs_make_dirs(dom_setup_path_join(root, "launcher"));
}

int dom_setup_cmd_install(const DomSetupInstallArgs &args)
{
    std::string install_root;
    if (args.mode == "portable") {
        install_root = dom_setup_portable_root_from_target(args.target);
    } else if (args.mode == "system") {
        install_root = args.target.empty() ? dom_setup_default_install_root_system() : args.target;
    } else {
        install_root = args.target.empty() ? dom_setup_default_install_root_per_user() : args.target;
    }

    DomInstallManifest manifest;
    manifest.schema_version = 1;
    manifest.install_id = dom_manifest_generate_uuid();
    manifest.install_type = args.mode.empty() ? "portable" : args.mode;
    manifest.platform = dom_manifest_platform_tag();
    manifest.version = args.version.empty() ? "0.0.0" : args.version;
    manifest.created_at = iso_now();
    manifest.created_by = "setup";

    if (!dom_fs_make_dirs(install_root)) {
        std::printf("Failed to create install root: %s\n", install_root.c_str());
        return 1;
    }
    ensure_minimal_layout(install_root);
    write_placeholder(install_root);

    std::string manifest_path = dom_setup_path_join(install_root, "dominium_install.json");
    std::string err;
    if (!dom_manifest_write(manifest_path, manifest, err)) {
        std::printf("Failed to write manifest: %s\n", err.c_str());
        return 1;
    }

    // Best-effort index registration (local config file).
    std::string index_path = dom_setup_install_index_path();
    dom_fs_make_dirs(dom_setup_user_config_root());
    FILE *idx = std::fopen(index_path.c_str(), "ab");
    if (idx) {
        std::fprintf(idx, "%s|%s|%s|%s\n",
                     manifest.install_id.c_str(),
                     install_root.c_str(),
                     manifest.install_type.c_str(),
                     manifest.version.c_str());
        std::fclose(idx);
    }

    std::printf("Installed Dominium (%s) at %s\n",
                manifest.install_type.c_str(),
                install_root.c_str());
    return 0;
}
