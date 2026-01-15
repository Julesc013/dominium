/*
FILE: source/dominium/setup/core/setup_paths.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/setup_paths
RESPONSIBILITY: Implements `setup_paths`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "setup_paths.h"
#include "dom_shared/os_paths.h"

#include <string>

using namespace dom_shared;

std::string setup_user_data_root_for_install(const std::string &install_type, const std::string &install_root)
{
    if (install_type == "portable") {
        return install_root;
    }
    return os_get_per_user_game_data_root();
}

std::string setup_launcher_db_path_for_install(const std::string &install_type, const std::string &install_root)
{
    if (install_type == "portable") {
        return os_path_join(os_path_join(install_root, "launcher"), "db.json");
    }
    return os_path_join(os_get_per_user_launcher_data_root(), "db.json");
}
