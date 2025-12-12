#include <cstdio>
#include <cstring>

#include "dom_setup_app.h"

namespace {

void print_usage() {
    std::printf("Usage: dominium-setup --install <path> | --repair <product> | --uninstall <product> | --import <path> | --gc | --validate <path> [--home=<dominium_home>]\n");
}

} // namespace

int main(int argc, char **argv) {
    dom::SetupConfig cfg;
    dom::DomSetupApp app;
    int i;

    cfg.home.clear();
    cfg.action.clear();
    cfg.target.clear();

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) continue;

        if (std::strncmp(arg, "--home=", 7) == 0) {
            cfg.home = arg + 7;
        } else if (std::strncmp(arg, "--install", 9) == 0) {
            cfg.action = "install";
            if (arg[9] == '=') {
                cfg.target = arg + 10;
            } else if (i + 1 < argc) {
                cfg.target = argv[++i];
            }
        } else if (std::strncmp(arg, "--repair", 8) == 0) {
            cfg.action = "repair";
            if (arg[8] == '=') {
                cfg.target = arg + 9;
            } else if (i + 1 < argc) {
                cfg.target = argv[++i];
            }
        } else if (std::strncmp(arg, "--uninstall", 11) == 0) {
            cfg.action = "uninstall";
            if (arg[11] == '=') {
                cfg.target = arg + 12;
            } else if (i + 1 < argc) {
                cfg.target = argv[++i];
            }
        } else if (std::strncmp(arg, "--import", 8) == 0) {
            cfg.action = "import";
            if (arg[8] == '=') {
                cfg.target = arg + 9;
            } else if (i + 1 < argc) {
                cfg.target = argv[++i];
            }
        } else if (std::strcmp(arg, "--gc") == 0) {
            cfg.action = "gc";
        } else if (std::strncmp(arg, "--validate", 10) == 0) {
            cfg.action = "validate";
            if (arg[10] == '=') {
                cfg.target = arg + 11;
            } else if (i + 1 < argc) {
                cfg.target = argv[++i];
            }
        }
    }

    if (cfg.action.empty()) {
        print_usage();
        return 1;
    }

    if (!app.init_from_cli(cfg)) {
        return 1;
    }

    app.run();
    app.shutdown();
    return 0;
}
