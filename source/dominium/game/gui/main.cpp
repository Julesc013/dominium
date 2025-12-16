/*
FILE: source/dominium/game/gui/main.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/gui/main
RESPONSIBILITY: Implements `main`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime_app.h"
#include "runtime_display.h"

#include <cstdio>
#include <cstring>
#include <string>

static void print_usage()
{
    std::printf("dom_main usage:\n");
    std::printf("  dom_main [--role=client|server|tool] [--display=none|cli|tui|gui|auto]\n");
    std::printf("           [--universe=PATH] [--launcher-session-id=GUID] [--launcher-instance-id=GUID]\n");
    std::printf("           [--launcher-integration=auto|off] [--version] [--capabilities] [--help]\n");
}

static bool arg_value(const char *arg, const char *key, std::string &out)
{
    size_t n = std::strlen(key);
    if (std::strncmp(arg, key, n) != 0) return false;
    if (arg[n] == '=' || arg[n] == ':') {
        out.assign(arg + n + 1);
        return true;
    }
    return false;
}

int main(int argc, char **argv)
{
    RuntimeConfig cfg;
    cfg.role = "client";
    cfg.display = "auto";
    cfg.universe_path = "saves/default";
    cfg.launcher_session_id = "";
    cfg.launcher_instance_id = "";
    cfg.launcher_integration = "auto";

    bool want_version = false;
    bool want_caps = false;
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--help") == 0 || std::strcmp(argv[i], "-h") == 0) {
            print_usage();
            return 0;
        } else if (std::strcmp(argv[i], "--version") == 0) {
            want_version = true;
        } else if (std::strcmp(argv[i], "--capabilities") == 0) {
            want_caps = true;
        } else if (arg_value(argv[i], "--role", cfg.role)) {
        } else if (arg_value(argv[i], "--display", cfg.display)) {
        } else if (arg_value(argv[i], "--universe", cfg.universe_path)) {
        } else if (arg_value(argv[i], "--launcher-session-id", cfg.launcher_session_id)) {
        } else if (arg_value(argv[i], "--launcher-instance-id", cfg.launcher_instance_id)) {
        } else if (arg_value(argv[i], "--launcher-integration", cfg.launcher_integration)) {
        }
    }

    if (want_version) {
        return runtime_print_version();
    }
    if (want_caps) {
        return runtime_print_capabilities();
    }

    return runtime_run(cfg);
}
