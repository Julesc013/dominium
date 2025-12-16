/*
FILE: source/dominium/launcher/core/launcher_discovery.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/launcher_discovery
RESPONSIBILITY: Implements `launcher_discovery`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher/launcher_discovery.h"
#include "dom_shared/os_paths.h"
#include "dom_shared/manifest_install.h"

#include <set>

namespace dom_launcher {

static void try_add_install(const dom_shared::InstallInfo& info,
                            std::vector<dom_shared::InstallInfo>& out,
                            std::set<std::string>& seen_ids,
                            std::set<std::string>& seen_roots)
{
    if (info.install_id.empty() && info.root_path.empty()) return;
    if (!info.install_id.empty() && seen_ids.find(info.install_id) != seen_ids.end()) return;
    if (!info.root_path.empty() && seen_roots.find(info.root_path) != seen_roots.end()) return;

    out.push_back(info);
    if (!info.install_id.empty()) seen_ids.insert(info.install_id);
    if (!info.root_path.empty()) seen_roots.insert(info.root_path);
}

std::vector<dom_shared::InstallInfo> discover_installs(const LauncherState& state)
{
    std::vector<dom_shared::InstallInfo> installs;
    std::set<std::string> seen_ids;
    std::set<std::string> seen_roots;

    if (!state.ctx.self_install.install_id.empty()) {
        try_add_install(state.ctx.self_install, installs, seen_ids, seen_roots);
    }

    if (!state.db.settings.enable_global_install_discovery && state.ctx.portable_mode) {
        return installs;
    }

    std::vector<std::string> roots = dom_shared::os_get_default_install_roots();
    for (size_t i = 0; i < state.db.manual_install_paths.size(); ++i) {
        roots.push_back(state.db.manual_install_paths[i]);
    }

    for (size_t i = 0; i < roots.size(); ++i) {
        const std::string& root = roots[i];
        if (!dom_shared::manifest_install_exists(root)) continue;
        dom_shared::InstallInfo info;
        if (dom_shared::parse_install_manifest(root, info)) {
            try_add_install(info, installs, seen_ids, seen_roots);
        }
    }
    return installs;
}

void merge_discovered_installs(LauncherState& state,
                               const std::vector<dom_shared::InstallInfo>& discovered)
{
    state.installs = discovered;

    for (size_t i = 0; i < discovered.size(); ++i) {
        const dom_shared::InstallInfo& info = discovered[i];
        bool updated = false;
        for (size_t j = 0; j < state.db.installs.size(); ++j) {
            if (!info.install_id.empty() && state.db.installs[j].install_id == info.install_id) {
                state.db.installs[j] = info;
                updated = true;
                break;
            }
            if (!info.root_path.empty() && state.db.installs[j].root_path == info.root_path) {
                state.db.installs[j] = info;
                updated = true;
                break;
            }
        }
        if (!updated) {
            state.db.installs.push_back(info);
        }
    }
}

} // namespace dom_launcher
