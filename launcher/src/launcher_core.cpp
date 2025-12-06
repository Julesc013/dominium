#include "launcher_core.h"

#include "launcher_logging.h"
#include "launcher_discovery.h"
#include "dom_setup_install_manifest.h"
#include "dom_setup_paths.h"

#include <cstdlib>
#include <sstream>

static std::string make_guid()
{
    return dom_manifest_generate_uuid();
}

LauncherInstall *launcher_find_install(LauncherContext &ctx, const std::string &install_id)
{
    for (size_t i = 0; i < ctx.discovered_installs.size(); ++i) {
        if (ctx.discovered_installs[i].install_id == install_id) {
            return &ctx.discovered_installs[i];
        }
    }
    return NULL;
}

bool launcher_refresh_installs(LauncherContext &ctx)
{
    ctx.discovered_installs.clear();
    launcher_discover_installs(ctx.discovered_installs);
    // Merge DB installs to keep user-added paths.
    for (size_t i = 0; i < ctx.db.installs.size(); ++i) {
        const LauncherInstall &inst = ctx.db.installs[i];
        bool found = false;
        for (size_t j = 0; j < ctx.discovered_installs.size(); ++j) {
            if (ctx.discovered_installs[j].install_root == inst.install_root) {
                found = true;
                break;
            }
        }
        if (!found) {
            ctx.discovered_installs.push_back(inst);
        }
    }
    ctx.db.installs = ctx.discovered_installs;
    launcher_db_save(ctx.db);
    return true;
}

bool launcher_init_context(LauncherContext &ctx, const std::string &preferred_install_root)
{
    std::string install_type = "per-user";
    if (!preferred_install_root.empty()) {
        DomInstallManifest manifest;
        std::string err;
        if (dom_manifest_read(dom_setup_path_join(preferred_install_root, "dominium_install.json"), manifest, err)) {
            install_type = manifest.install_type;
        }
    }
    ctx.launcher_db_path = dom_setup_launcher_db_path(install_type, preferred_install_root);
    launcher_db_load(ctx.launcher_db_path, ctx.db);
    ctx.db.path = ctx.launcher_db_path;
    return launcher_refresh_installs(ctx);
}

bool launcher_start_instance(LauncherContext &ctx,
                             const LauncherInstall &install,
                             const std::string &runtime_exe,
                             const std::vector<std::string> &args,
                             const std::string &role,
                             const std::string &display_mode,
                             LauncherInstance &out_instance,
                             std::string &err)
{
    std::vector<std::string> full_args = args;
    std::string session_id = make_guid();
    std::string instance_id = make_guid();

    if (!role.empty()) {
        full_args.push_back("--role=" + role);
    }
    if (!display_mode.empty()) {
        full_args.push_back("--display=" + display_mode);
    }
    full_args.push_back(std::string("--launcher-session-id=") + session_id);
    full_args.push_back(std::string("--launcher-instance-id=") + instance_id);

    LauncherProcessHandle handle;
    std::string workdir = install.install_root;
    if (!launcher_spawn_process(runtime_exe, full_args, workdir, display_mode != "gui", handle, err)) {
        return false;
    }
    handle.instance_id = instance_id;
    LauncherInstance inst;
    inst.process = handle;
    inst.install_id = install.install_id;
    inst.role = role;
    inst.display_mode = display_mode;
    inst.exe_path = runtime_exe;
    ctx.instances.push_back(inst);
    launcher_log_info("Started instance " + instance_id + " (" + role + ")");
    out_instance = inst;
    return true;
}

bool launcher_stop_instance(LauncherContext &ctx, const std::string &instance_id)
{
    for (size_t i = 0; i < ctx.instances.size(); ++i) {
        if (ctx.instances[i].process.instance_id == instance_id) {
            launcher_terminate_process(ctx.instances[i].process);
            ctx.instances.erase(ctx.instances.begin() + i);
            launcher_log_info("Stopped instance " + instance_id);
            return true;
        }
    }
    return false;
}
