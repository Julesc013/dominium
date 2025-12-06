#include "dom_setup_config.h"
#include "setup_paths.h"
#include "setup_registration.h"
#include "setup_plugins.h"
#include "dom_shared/manifest_install.h"
#include "dom_shared/logging.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/uuid.h"

#include <cstdio>
#include <vector>
#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#endif

static bool ensure_dir(const std::string &path)
{
    if (path.empty()) return false;
#ifdef _WIN32
    _mkdir(path.c_str());
#else
    mkdir(path.c_str(), 0755);
#endif
    FILE *f = std::fopen((path + "/.tmp").c_str(), "wb");
    if (f) {
        std::fclose(f);
        std::remove((path + "/.tmp").c_str());
        return true;
    }
    return false;
}

static void make_layout(const std::string &root)
{
    ensure_dir(root);
    ensure_dir(os_path_join(root, "bin"));
    ensure_dir(os_path_join(root, "data"));
    ensure_dir(os_path_join(root, "mods"));
    ensure_dir(os_path_join(root, "launcher"));
}

int run_install(const SetupConfig &cfg)
{
    SetupConfig mutable_cfg = cfg;
    setup_plugins_load();
    setup_plugins_apply_profiles(mutable_cfg);

    make_layout(mutable_cfg.install_root);

    InstallInfo info;
    info.install_id = generate_uuid();
    info.install_type = mutable_cfg.mode;
    info.platform = os_get_platform_id();
    info.version = mutable_cfg.version;
    info.root_path = mutable_cfg.install_root;
    info.created_by = "setup";

    bool ok = false;
    std::string err;
    write_install_manifest(info, ok, err);
    if (!ok) {
        log_error("failed to write manifest: " + err);
        return 1;
    }

    if (mutable_cfg.register_system) {
        register_install_with_system(info);
    }
    if (mutable_cfg.create_shortcuts) {
        create_shortcuts_for_install(info);
    }

    setup_plugins_post_install(info);
    setup_plugins_unload();

    log_info("install completed at " + mutable_cfg.install_root);
    return 0;
}
