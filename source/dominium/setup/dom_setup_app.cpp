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
