/*
FILE: tests/dominium_integration/setup_flow_test.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/dominium_integration
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <string>

#include "dom_setup_config.h"
#include "dom_shared/os_paths.h"

using namespace dom_shared;

int main(void)
{
    SetupConfig cfg;
    cfg.command = "install";
    cfg.mode = "portable";
    cfg.install_root = os_path_join(os_get_default_portable_install_root(), "tests_tmp_setup_install");
    cfg.version = "0.0.test";
    cfg.create_shortcuts = false;
    cfg.register_system = false;
    cfg.portable_self_contained = true;
    cfg.interactive = false;
    cfg.config_file = "";
    cfg.remove_user_data_on_uninstall = true;

    if (run_install(cfg) != 0) {
        std::printf("install command failed\n");
        return 1;
    }
    cfg.command = "info";
    if (run_info(cfg) != 0) {
        std::printf("info command failed\n");
        return 1;
    }
    cfg.command = "repair";
    if (run_repair(cfg) != 0) {
        std::printf("repair command failed\n");
        return 1;
    }
    cfg.command = "uninstall";
    if (run_uninstall(cfg) != 0) {
        std::printf("uninstall command failed\n");
        return 1;
    }
    std::printf("setup flow test passed\n");
    return 0;
}
