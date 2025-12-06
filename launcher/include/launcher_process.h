#ifndef DOM_LAUNCHER_PROCESS_H
#define DOM_LAUNCHER_PROCESS_H

#include "launcher_context.h"

#include <string>
#include <vector>

enum DomDisplayMode {
    DOM_DISPLAY_NONE = 0,
    DOM_DISPLAY_CLI  = 1,
    DOM_DISPLAY_TUI  = 2,
    DOM_DISPLAY_GUI  = 3
};

struct Instance {
    std::string instance_id;
    InstallInfo install;
    std::string role;
    DomDisplayMode display_mode;
    std::string universe_path;
    std::string profile_id;
    std::string mods_hash;
    int pid;
    std::string state;
    std::string log_path;
    double start_time_utc;
    double stop_time_utc;
};

struct RuntimeCapabilities {
    std::string binary_id;
    std::string binary_version;
    std::string engine_version;
    std::vector<std::string> roles;
    std::vector<std::string> display_modes;
    std::vector<int> save_versions;
    std::vector<int> content_pack_versions;
};

Instance start_instance(const LauncherContext &ctx,
                        const InstallInfo &install,
                        const std::string &role,
                        DomDisplayMode display,
                        const std::string &universe_path,
                        const std::string &profile_id,
                        const std::string &mods_hash);

bool stop_instance(const std::string &instance_id);
Instance *get_instance(const std::string &instance_id);
std::vector<Instance> list_instances();
RuntimeCapabilities query_runtime_capabilities(const InstallInfo &install);

#endif /* DOM_LAUNCHER_PROCESS_H */
