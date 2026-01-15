/*
FILE: source/dominium/setup/core/setup_registration.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/setup_registration
RESPONSIBILITY: Implements `setup_registration`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "setup_registration.h"
#include "dom_shared/logging.h"

using namespace dom_shared;

void register_install_with_system(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("register_install_with_system: stub (platform-specific registration not implemented)");
}

void unregister_install_from_system(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("unregister_install_from_system: stub");
}

void create_shortcuts_for_install(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("create_shortcuts_for_install: stub");
}

void remove_shortcuts_for_install(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("remove_shortcuts_for_install: stub");
}
