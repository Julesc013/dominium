/*
FILE: source/dominium/launcher/core/launcher_context.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/launcher_context
RESPONSIBILITY: Implements `launcher_context`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher/launcher_context.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/manifest_install.h"
#include "dom_shared/logging.h"
#include "dom_shared/uuid.h"

#include <algorithm>
#include <cctype>

namespace dom_launcher {

static LauncherContext g_ctx;
static bool g_ctx_inited = false;

static bool path_contains_ci(const std::string& haystack, const std::string& needle)
{
    std::string h = haystack;
    std::string n = needle;
    for (size_t i = 0; i < h.size(); ++i) h[i] = (char)std::tolower((unsigned char)h[i]);
    for (size_t i = 0; i < n.size(); ++i) n[i] = (char)std::tolower((unsigned char)n[i]);
    return h.find(n) != std::string::npos;
}

static std::string infer_install_type(const std::string& exe_dir)
{
    std::string platform = dom_shared::os_get_platform_id();
    if (platform == "win_nt") {
        if (path_contains_ci(exe_dir, "program files")) return "system";
    } else if (platform == "linux") {
        if (exe_dir.find("/opt/") == 0 || exe_dir == "/opt" || path_contains_ci(exe_dir, "/opt/dominium")) return "system";
    } else if (platform == "mac") {
        if (path_contains_ci(exe_dir, "/applications/")) return "system";
    }
    std::string home = dom_shared::os_get_per_user_game_data_root();
    if (!home.empty() && path_contains_ci(exe_dir, home)) {
        return "per-user";
    }
    return "portable";
}

LauncherContext init_launcher_context()
{
    if (g_ctx_inited) return g_ctx;

    std::string exe_dir = dom_shared::os_get_executable_directory();
    dom_shared::InstallInfo info;
    if (dom_shared::manifest_install_exists(exe_dir)) {
        if (!dom_shared::parse_install_manifest(exe_dir, info)) {
            dom_shared::log_warn("failed to parse self manifest, using synthetic install");
        }
    }
    if (info.install_id.empty()) {
        info.install_id = dom_shared::generate_uuid();
        info.install_type = infer_install_type(exe_dir);
        info.platform = dom_shared::os_get_platform_id();
        info.version = "unknown";
        info.root_path = exe_dir;
        info.created_at = "";
        info.created_by = "unknown";
    }

    g_ctx.self_install = info;
    g_ctx.portable_mode = (info.install_type == "portable");
    if (g_ctx.portable_mode) {
        g_ctx.user_data_root = dom_shared::os_path_join(info.root_path, "launcher");
    } else {
        g_ctx.user_data_root = dom_shared::os_get_per_user_launcher_data_root();
    }
    dom_shared::os_ensure_directory_exists(g_ctx.user_data_root);
    g_ctx.session_id = dom_shared::generate_uuid();

    g_ctx_inited = true;
    return g_ctx;
}

const LauncherContext& get_launcher_context()
{
    if (!g_ctx_inited) {
        init_launcher_context();
    }
    return g_ctx;
}

} // namespace dom_launcher
