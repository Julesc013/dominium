/*
FILE: source/dominium/launcher/core/launcher_process.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/launcher_process
RESPONSIBILITY: Implements `launcher_process`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "launcher_process.h"
#include "launcher_logging.h"
#include "dom_shared/uuid.h"
#include "dom_shared/os_paths.h"

#include <ctime>
#include <vector>
#include <sstream>
#include <cstdio>

static std::vector<Instance> g_instances;

static double now_utc()
{
    return (double)std::time(0);
}

Instance start_instance(const LauncherContext &ctx,
                        const dom_shared::InstallInfo &install,
                        const std::string &role,
                        DomDisplayMode display,
                        const std::string &universe_path,
                        const std::string &profile_id,
                        const std::string &mods_hash)
{
    Instance inst;
    inst.instance_id = dom_shared::generate_uuid();
    inst.install = install;
    inst.role = role;
    inst.display_mode = display;
    inst.universe_path = universe_path;
    inst.profile_id = profile_id;
    inst.mods_hash = mods_hash;
    inst.pid = -1;
    inst.state = "running";
    inst.start_time_utc = now_utc();
    inst.stop_time_utc = 0.0;
    inst.log_path = dom_shared::os_path_join(dom_shared::os_path_join(ctx.user_data_root, "runtime_logs"), inst.instance_id + ".log");

    FILE *f = fopen(inst.log_path.c_str(), "wb");
    if (f) {
        std::fprintf(f, "Started instance %s role=%s display=%d universe=%s\n",
                     inst.instance_id.c_str(), role.c_str(), (int)display, universe_path.c_str());
        std::fclose(f);
    }
    g_instances.push_back(inst);
    launcher_log_info("started instance " + inst.instance_id + " (stub, no process)");
    return inst;
}

bool stop_instance(const std::string &instance_id)
{
    for (size_t i = 0; i < g_instances.size(); ++i) {
        if (g_instances[i].instance_id == instance_id) {
            g_instances[i].state = "stopped";
            g_instances[i].stop_time_utc = now_utc();
            launcher_log_info("stopped instance " + instance_id);
            return true;
        }
    }
    return false;
}

Instance *get_instance(const std::string &instance_id)
{
    for (size_t i = 0; i < g_instances.size(); ++i) {
        if (g_instances[i].instance_id == instance_id) {
            return &g_instances[i];
        }
    }
    return 0;
}

RuntimeCapabilities query_runtime_capabilities(const dom_shared::InstallInfo &install)
{
    RuntimeCapabilities caps;
    caps.binary_id = "unknown";
    caps.binary_version = install.version;
    caps.engine_version = "unknown";
    caps.roles.push_back("client");
    caps.display_modes.push_back("gui");
    caps.display_modes.push_back("cli");
    caps.display_modes.push_back("tui");
    caps.display_modes.push_back("none");
    caps.save_versions.push_back(1);
    caps.content_pack_versions.push_back(1);
    return caps;
}
