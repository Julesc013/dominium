/*
FILE: source/dominium/setup/cli/setup_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/cli/setup_cli
RESPONSIBILITY: Implements `setup_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "setup_cli.h"
#include "dom_shared/logging.h"
#include "dom_shared/json.h"
#include "dom_shared/os_paths.h"

#include <string>
#include <cstdio>
#include <cstring>

#ifdef _WIN32
#include <io.h>
#define ISATTY _isatty
#define FILENO _fileno
#define STDIN_FILENO 0
#else
#include <unistd.h>
#define ISATTY isatty
#define FILENO fileno
#endif

using namespace dom_shared;

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

bool is_stdin_interactive()
{
    return ISATTY(FILENO(stdin)) != 0;
}

void print_usage()
{
    std::printf("dom_setup commands:\n");
    std::printf("  install   [--mode=portable|per-user|system] [--install-root=PATH] [--version=X.Y.Z]\n");
    std::printf("            [--no-shortcuts] [--no-register-system] [--config=FILE] [--non-interactive]\n");
    std::printf("  repair    --install-root=PATH\n");
    std::printf("  uninstall --install-root=PATH [--remove-user-data]\n");
    std::printf("  list\n");
    std::printf("  info      --install-root=PATH\n");
}

static void apply_flag_overrides(SetupConfig &cfg, int argc, char **argv)
{
    for (int i = 2; i < argc; ++i) {
        std::string val;
        if (arg_value(argv[i], "--mode", val)) {
            cfg.mode = val;
        } else if (arg_value(argv[i], "--install-root", val)) {
            cfg.install_root = val;
        } else if (arg_value(argv[i], "--version", val)) {
            cfg.version = val;
        } else if (arg_value(argv[i], "--config", val)) {
            cfg.config_file = val;
        } else if (std::strcmp(argv[i], "--no-shortcuts") == 0) {
            cfg.create_shortcuts = false;
        } else if (std::strcmp(argv[i], "--no-register-system") == 0) {
            cfg.register_system = false;
        } else if (std::strcmp(argv[i], "--non-interactive") == 0) {
            cfg.interactive = false;
        } else if (std::strcmp(argv[i], "--remove-user-data") == 0) {
            cfg.remove_user_data_on_uninstall = true;
        }
    }
}

bool parse_setup_cli(int argc, char **argv, SetupConfig &cfg)
{
    if (argc < 2) {
        print_usage();
        return false;
    }
    cfg.interactive = is_stdin_interactive();
    cfg.command = argv[1];
    apply_flag_overrides(cfg, argc, argv);
    if (cfg.command == "install" || cfg.command == "repair" || cfg.command == "uninstall" || cfg.command == "list" || cfg.command == "info") {
        return true;
    }
    print_usage();
    return false;
}

void load_setup_config_file(SetupConfig &cfg)
{
    if (cfg.config_file.empty()) return;
    FILE *f = std::fopen(cfg.config_file.c_str(), "rb");
    if (!f) {
        log_warn("could not open config file");
        return;
    }
    std::string content;
    char buf[512];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) content.append(buf, n);
    std::fclose(f);
    JsonValue root;
    if (!json_parse(content, root) || root.type() != JsonValue::Object) {
        log_warn("invalid config file");
        return;
    }
    if (root.has("mode")) cfg.mode = root["mode"].as_string(cfg.mode);
    if (root.has("install_root")) cfg.install_root = root["install_root"].as_string(cfg.install_root);
    if (root.has("version")) cfg.version = root["version"].as_string(cfg.version);
}

void apply_cli_overrides(SetupConfig &cfg, int argc, char **argv)
{
    apply_flag_overrides(cfg, argc, argv);
}

bool resolve_setup_defaults(SetupConfig &cfg)
{
    if (cfg.mode.empty()) {
        cfg.mode = cfg.interactive ? "per-user" : "per-user";
    }
    if (cfg.mode == "portable") {
        cfg.portable_self_contained = true;
        cfg.register_system = false;
        cfg.create_shortcuts = false;
    } else if (cfg.mode == "system") {
        cfg.register_system = true;
        cfg.create_shortcuts = true;
    } else {
        cfg.register_system = false;
        cfg.create_shortcuts = true;
    }

    if (cfg.install_root.empty()) {
        if (cfg.mode == "portable") {
            cfg.install_root = os_get_default_portable_install_root();
        } else if (cfg.mode == "system") {
            cfg.install_root = os_get_default_system_install_root();
        } else {
            cfg.install_root = os_get_default_per_user_install_root();
        }
    }
    return !cfg.install_root.empty();
}
