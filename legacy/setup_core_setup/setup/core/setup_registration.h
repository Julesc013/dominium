/*
FILE: source/dominium/setup/core/setup_registration.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/setup_registration
RESPONSIBILITY: Defines internal contract for `setup_registration`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SETUP_REGISTRATION_H
#define DOM_SETUP_REGISTRATION_H

#include "dom_shared/manifest_install.h"

void register_install_with_system(const dom_shared::InstallInfo &info);
void unregister_install_from_system(const dom_shared::InstallInfo &info);
void create_shortcuts_for_install(const dom_shared::InstallInfo &info);
void remove_shortcuts_for_install(const dom_shared::InstallInfo &info);

#endif /* DOM_SETUP_REGISTRATION_H */
