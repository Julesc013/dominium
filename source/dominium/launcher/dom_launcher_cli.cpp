#include <cstdio>
#include <cstring>

#include "dom_launcher_app.h"
#include "dom_profile_cli.h"

namespace {

dom::LauncherMode parse_mode(const char *text, dom::LauncherMode def_mode) {
    if (!text) {
        return def_mode;
    }
    if (std::strcmp(text, "gui") == 0) return dom::LAUNCHER_MODE_GUI;
    if (std::strcmp(text, "tui") == 0) return dom::LAUNCHER_MODE_TUI;
    if (std::strcmp(text, "cli") == 0) return dom::LAUNCHER_MODE_CLI;
    return def_mode;
}

} // namespace

int main(int argc, char **argv) {
    dom::LauncherConfig cfg;
    dom::DomLauncherApp app;
    dom::ProfileCli profile_cli;
    std::string profile_err;
    int i;

    dom::init_default_profile_cli(profile_cli);
    if (!dom::parse_profile_cli_args(argc, argv, profile_cli, profile_err)) {
        std::fprintf(stderr, "Error: %s\n", profile_err.c_str());
        return 2;
    }
    if (profile_cli.print_caps) {
        dom::print_caps(stdout);
        return 0;
    }
    if (profile_cli.print_selection) {
        dom::print_caps(stdout);
        return dom::print_selection(profile_cli.profile, stdout, stderr);
    }

    cfg.home.clear();
    cfg.mode = dom::LAUNCHER_MODE_GUI;
    cfg.action.clear();
    cfg.instance_id.clear();
    cfg.product.clear();
    cfg.product_mode = "gui";

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) {
            continue;
        }
        if (std::strncmp(arg, "--home=", 7) == 0) {
            cfg.home = arg + 7;
        } else if (std::strncmp(arg, "--mode=", 7) == 0) {
            cfg.mode = parse_mode(arg + 7, cfg.mode);
        } else if (std::strncmp(arg, "--product-mode=", 16) == 0) {
            cfg.product_mode = arg + 16;
        } else if (std::strncmp(arg, "--action=", 9) == 0) {
            cfg.action = arg + 9;
        } else if (std::strncmp(arg, "--instance=", 11) == 0) {
            cfg.instance_id = arg + 11;
        } else if (std::strncmp(arg, "--product=", 10) == 0) {
            cfg.product = arg + 10;
        }
    }

    if (!app.init_from_cli(cfg)) {
        std::printf("Launcher: failed to initialize.\n");
        return 1;
    }

    app.run();
    app.shutdown();
    return 0;
}
