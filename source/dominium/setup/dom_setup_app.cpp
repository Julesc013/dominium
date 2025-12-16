/*
FILE: source/dominium/setup/dom_setup_app.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/dom_setup_app
RESPONSIBILITY: Implements `dom_setup_app`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_setup_app.h"

#include <cstdio>

#include "dom_setup_ops.h"

namespace dom {

DomSetupApp::DomSetupApp() {
}

DomSetupApp::~DomSetupApp() {
    shutdown();
}

bool DomSetupApp::init_from_cli(const SetupConfig &cfg) {
    std::string home = cfg.home;
    if (home.empty()) {
        home = ".";
    }
    if (!resolve_paths(m_paths, home)) {
        std::printf("setup: failed to resolve DOMINIUM_HOME from '%s'\n", home.c_str());
        return false;
    }
    return perform_action(cfg);
}

void DomSetupApp::run() {
    /* CLI is synchronous; nothing extra to run here. */
}

void DomSetupApp::shutdown() {
    /* No persistent state yet. */
}

bool DomSetupApp::perform_action(const SetupConfig &cfg) {
    if (cfg.action == "install") {
        return setup_install(m_paths, cfg.target);
    }
    if (cfg.action == "repair") {
        return setup_repair(m_paths, cfg.target);
    }
    if (cfg.action == "uninstall") {
        return setup_uninstall(m_paths, cfg.target);
    }
    if (cfg.action == "import") {
        return setup_import(m_paths, cfg.target);
    }
    if (cfg.action == "gc") {
        return setup_gc(m_paths);
    }
    if (cfg.action == "validate") {
        return setup_validate(m_paths, cfg.target);
    }

    std::printf("setup: unsupported action '%s'\n", cfg.action.c_str());
    return false;
}

} // namespace dom
