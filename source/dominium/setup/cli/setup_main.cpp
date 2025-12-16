/*
FILE: source/dominium/setup/cli/setup_main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/cli/setup_main
RESPONSIBILITY: Implements `setup_main`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_setup/dom_setup_config.h"
#include "dom_shared/logging.h"

#include <cstdlib>
#include <cstring>

using namespace dom_shared;

int main(int argc, char **argv)
{
    SetupConfig cfg;
    cfg.command = "";
    cfg.mode = "";
    cfg.install_root = "";
    cfg.version = "0.0.0";
    cfg.create_shortcuts = true;
    cfg.register_system = false;
    cfg.portable_self_contained = false;
    cfg.interactive = true;
    cfg.config_file = "";
    cfg.remove_user_data_on_uninstall = false;

    if (!parse_setup_cli(argc, argv, cfg)) {
        return 1;
    }

    load_setup_config_file(cfg);
    apply_cli_overrides(cfg, argc, argv);

    if (!resolve_setup_defaults(cfg)) {
        log_error("failed to resolve defaults; specify --mode/--install-root");
        return 1;
    }

    if (cfg.command == "install") {
        return run_install(cfg);
    } else if (cfg.command == "repair") {
        return run_repair(cfg);
    } else if (cfg.command == "uninstall") {
        return run_uninstall(cfg);
    } else if (cfg.command == "list") {
        return run_list(cfg);
    } else if (cfg.command == "info") {
        return run_info(cfg);
    }

    log_error("unknown command");
    return 1;
}
