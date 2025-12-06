#include "dom_setup_cli.h"

#include <cstdio>
#include <cstring>
#include <string>

static bool arg_match(const char *arg, const char *name, std::string &out)
{
    size_t n = std::strlen(name);
    if (std::strncmp(arg, name, n) != 0) return false;
    if (arg[n] == '=') {
        out.assign(arg + n + 1);
        return true;
    }
    return false;
}

void dom_setup_print_usage()
{
    std::printf("dom_setup commands:\n");
    std::printf("  install   --mode=portable|per-user|system --target=<path> [--version=X.Y.Z]\n");
    std::printf("  repair    --install-root=<path>\n");
    std::printf("  uninstall --install-root=<path> [--remove-user-data]\n");
    std::printf("  list\n");
    std::printf("  info      --install-root=<path>\n");
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        dom_setup_print_usage();
        return 1;
    }
    std::string cmd = argv[1];
    if (cmd == "install") {
        DomSetupInstallArgs args;
        args.mode = "portable";
        for (int i = 2; i < argc; ++i) {
            std::string val;
            if (arg_match(argv[i], "--mode", val)) {
                args.mode = val;
            } else if (arg_match(argv[i], "--target", val)) {
                args.target = val;
            } else if (arg_match(argv[i], "--version", val)) {
                args.version = val;
            }
        }
        return dom_setup_cmd_install(args);
    } else if (cmd == "repair") {
        std::string root;
        for (int i = 2; i < argc; ++i) {
            std::string val;
            if (arg_match(argv[i], "--install-root", val)) {
                root = val;
            }
        }
        if (root.empty()) {
            std::printf("repair requires --install-root\n");
            dom_setup_print_usage();
            return 1;
        }
        return dom_setup_cmd_repair(root);
    } else if (cmd == "uninstall") {
        std::string root;
        bool remove_user_data = false;
        for (int i = 2; i < argc; ++i) {
            std::string val;
            if (arg_match(argv[i], "--install-root", val)) {
                root = val;
            } else if (std::strcmp(argv[i], "--remove-user-data") == 0) {
                remove_user_data = true;
            }
        }
        if (root.empty()) {
            std::printf("uninstall requires --install-root\n");
            dom_setup_print_usage();
            return 1;
        }
        return dom_setup_cmd_uninstall(root, remove_user_data);
    } else if (cmd == "list") {
        return dom_setup_cmd_list();
    } else if (cmd == "info") {
        std::string root;
        for (int i = 2; i < argc; ++i) {
            std::string val;
            if (arg_match(argv[i], "--install-root", val)) {
                root = val;
            }
        }
        if (root.empty()) {
            std::printf("info requires --install-root\n");
            dom_setup_print_usage();
            return 1;
        }
        return dom_setup_cmd_info(root);
    }
    dom_setup_print_usage();
    return 1;
}
