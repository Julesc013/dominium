/*
FILE: source/dominium/setup/core/setup_run_info.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/setup_run_info
RESPONSIBILITY: Implements `setup_run_info`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_setup/dom_setup_config.h"
#include "dom_shared/manifest_install.h"
#include "dom_shared/logging.h"
#include "dom_shared/os_paths.h"

#include <cstdio>
#include <vector>

using namespace dom_shared;

static void discover_in_root(const std::string &root, std::vector<InstallInfo> &out)
{
    if (manifest_install_exists(root)) {
        InstallInfo info;
        if (parse_install_manifest(root, info)) {
            out.push_back(info);
        }
    }
}

int run_list(const SetupConfig &cfg)
{
    (void)cfg;
    std::vector<InstallInfo> installs;
    discover_in_root(os_get_default_per_user_install_root(), installs);
    discover_in_root(os_get_default_system_install_root(), installs);
    discover_in_root(os_get_default_portable_install_root(), installs);
    for (size_t i = 0; i < installs.size(); ++i) {
        std::printf("%s | %s | %s | %s\n",
                    installs[i].root_path.c_str(),
                    installs[i].install_type.c_str(),
                    installs[i].platform.c_str(),
                    installs[i].install_id.c_str());
    }
    if (installs.empty()) {
        std::printf("No installs found\n");
    }
    return 0;
}

int run_info(const SetupConfig &cfg)
{
    InstallInfo info;
    if (!parse_install_manifest(cfg.install_root, info)) {
        log_error("info failed: could not parse manifest");
        return 1;
    }
    std::printf("{\"install_id\":\"%s\",\"install_type\":\"%s\",\"platform\":\"%s\",\"version\":\"%s\",\"root_path\":\"%s\"}\n",
                info.install_id.c_str(),
                info.install_type.c_str(),
                info.platform.c_str(),
                info.version.c_str(),
                info.root_path.c_str());
    return 0;
}
