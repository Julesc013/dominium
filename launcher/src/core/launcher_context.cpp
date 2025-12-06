#include "launcher_context.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/manifest_install.h"
#include "dom_shared/logging.h"
#include "dom_shared/uuid.h"

#include <sys/stat.h>
#ifdef _WIN32
#include <direct.h>
#endif

static LauncherContext g_ctx;
static bool g_ctx_inited = false;

static bool file_exists(const std::string &path)
{
    FILE *f = std::fopen(path.c_str(), "rb");
    if (f) { std::fclose(f); return true; }
    return false;
}

static void ensure_dir(const std::string &path)
{
#ifdef _WIN32
    _mkdir(path.c_str());
#else
    mkdir(path.c_str(), 0755);
#endif
}

LauncherContext init_launcher_context()
{
    if (g_ctx_inited) return g_ctx;
    std::string exe_dir = os_get_executable_directory();
    std::string manifest_path = os_path_join(exe_dir, "dominium_install.json");

    bool ok = false;
    std::string err;
    if (file_exists(manifest_path)) {
        g_ctx.self_install = parse_install_manifest(exe_dir, ok, err);
        if (!ok) {
            log_warn("failed to parse self manifest, using synthetic install");
        }
    }
    if (!ok) {
        g_ctx.self_install.install_id = generate_uuid();
        g_ctx.self_install.install_type = "portable";
        g_ctx.self_install.platform = os_get_platform_id();
        g_ctx.self_install.version = "unknown";
        g_ctx.self_install.root_path = exe_dir;
        g_ctx.self_install.created_by = "launcher";
    }

    g_ctx.portable_mode = (g_ctx.self_install.install_type == "portable");
    if (g_ctx.portable_mode) {
        g_ctx.user_data_root = os_path_join(g_ctx.self_install.root_path, "launcher");
    } else {
        g_ctx.user_data_root = os_get_per_user_launcher_data_root();
    }
    ensure_dir(g_ctx.user_data_root);
    ensure_dir(os_path_join(g_ctx.user_data_root, "runtime_logs"));

    g_ctx.session_id = generate_uuid();
    g_ctx_inited = true;
    return g_ctx;
}

const LauncherContext &get_launcher_context()
{
    if (!g_ctx_inited) {
        init_launcher_context();
    }
    return g_ctx;
}
