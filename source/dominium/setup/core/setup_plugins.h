/*
FILE: source/dominium/setup/core/setup_plugins.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/setup_plugins
RESPONSIBILITY: Implements `setup_plugins`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SETUP_PLUGINS_H
#define DOM_SETUP_PLUGINS_H

#include "dom_setup_plugin.h"
#include "dom_shared/manifest_install.h"
#include "dom_setup/dom_setup_config.h"

#include <vector>
#include <string>

void setup_plugins_load();
void setup_plugins_unload();
void setup_plugins_apply_profiles(SetupConfig &cfg);
void setup_plugins_post_install(const dom_shared::InstallInfo &info);
void setup_plugins_post_repair(const dom_shared::InstallInfo &info);
void setup_plugins_post_uninstall(const dom_shared::InstallInfo &info);

#endif /* DOM_SETUP_PLUGINS_H */
