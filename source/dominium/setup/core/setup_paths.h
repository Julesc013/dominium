/*
FILE: source/dominium/setup/core/setup_paths.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/setup_paths
RESPONSIBILITY: Defines internal contract for `setup_paths`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SETUP_PATHS_H
#define DOM_SETUP_PATHS_H

#include <string>

std::string setup_user_data_root_for_install(const std::string &install_type, const std::string &install_root);
std::string setup_launcher_db_path_for_install(const std::string &install_type, const std::string &install_root);

#endif /* DOM_SETUP_PATHS_H */
