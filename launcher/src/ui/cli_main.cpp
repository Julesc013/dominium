#include "launcher_core.h"
#include "launcher_logging.h"
#include "dom_setup_cli.h"
#include "dom_setup_paths.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <cstdlib>

static bool parse_arg(const char *arg, const char *key, std::string &out)
{
    size_t n = std::strlen(key);
    if (std::strncmp(arg, key, n) != 0) return false;
    if (arg[n] == '=' || arg[n] == ':') {
        out.assign(arg + n + 1);
        return true;
    }
    return false;
}

static void print_cli_usage()
{
    std::printf("dom_launcher CLI\n");
    std::printf("Usage:\n");
    std::printf("  dom_launcher installs list\n");
    std::printf("  dom_launcher installs info --install-id=<id>\n");
    std::printf("  dom_launcher installs repair --install-root=<path>\n");
    std::printf("  dom_launcher instances start --install-id=<id> [--exe=<path>] [--role=client|server|tool] [--display=gui|tui|cli|none]\n");
    std::printf("  dom_launcher instances stop --id=<instance-id>\n");
    std::printf("See docs/API/LAUNCHER_CLI.md for details.\n");
}

static bool call_dom_setup_repair(const std::string &root)
{
    std::string cmd = "dom_setup repair --install-root=" + root;
    int rc = std::system(cmd.c_str());
    return rc == 0;
}

int launcher_run_cli(int argc, char **argv)
{
    if (argc < 2) {
        print_cli_usage();
        return 0;
    }

    LauncherContext ctx;
    launcher_init_context(ctx, "");

    std::string group = argv[1];
    if (group == std::string("installs")) {
        if (argc < 3) {
            print_cli_usage();
            return 1;
        }
        std::string action = argv[2];
        if (action == std::string("list")) {
            for (size_t i = 0; i < ctx.discovered_installs.size(); ++i) {
                const LauncherInstall &inst = ctx.discovered_installs[i];
                std::printf("%s | %s | %s | %s\n",
                            inst.install_id.c_str(),
                            inst.install_root.c_str(),
                            inst.install_type.c_str(),
                            inst.version.c_str());
            }
            if (ctx.discovered_installs.empty()) {
                std::printf("No installs found\n");
            }
            return 0;
        } else if (action == std::string("info")) {
            std::string install_id;
            for (int i = 3; i < argc; ++i) {
                parse_arg(argv[i], "--install-id", install_id);
            }
            if (install_id.empty()) {
                std::printf("info requires --install-id\n");
                return 1;
            }
            LauncherInstall *inst = launcher_find_install(ctx, install_id);
            if (!inst) {
                std::printf("install not found: %s\n", install_id.c_str());
                return 1;
            }
            std::printf("install_id: %s\nroot: %s\ntype: %s\nplatform: %s\nversion: %s\n",
                        inst->install_id.c_str(),
                        inst->install_root.c_str(),
                        inst->install_type.c_str(),
                        inst->platform.c_str(),
                        inst->version.c_str());
            return 0;
        } else if (action == std::string("repair")) {
            std::string root;
            for (int i = 3; i < argc; ++i) {
                parse_arg(argv[i], "--install-root", root);
            }
            if (root.empty()) {
                std::printf("repair requires --install-root\n");
                return 1;
            }
            if (!call_dom_setup_repair(root)) {
                std::printf("repair failed for %s\n", root.c_str());
                return 1;
            }
            launcher_refresh_installs(ctx);
            return 0;
        }
    } else if (group == std::string("instances")) {
        if (argc < 3) {
            print_cli_usage();
            return 1;
        }
        std::string action = argv[2];
        if (action == std::string("start")) {
            std::string install_id;
            std::string exe;
            std::string role = "client";
            std::string display = "gui";
            for (int i = 3; i < argc; ++i) {
                parse_arg(argv[i], "--install-id", install_id);
                parse_arg(argv[i], "--exe", exe);
                parse_arg(argv[i], "--role", role);
                parse_arg(argv[i], "--display", display);
            }
            if (install_id.empty()) {
                std::printf("start requires --install-id\n");
                return 1;
            }
            LauncherInstall *inst = launcher_find_install(ctx, install_id);
            if (!inst) {
                std::printf("install not found: %s\n", install_id.c_str());
                return 1;
            }
            if (exe.empty()) {
                exe = dom_setup_path_join(inst->install_root, "bin/dom_cli");
            }
            std::vector<std::string> args;
            LauncherInstance launched;
            std::string err;
            if (!launcher_start_instance(ctx, *inst, exe, args, role, display, launched, err)) {
                std::printf("failed to start instance: %s\n", err.c_str());
                return 1;
            }
            std::printf("started instance %s (pid %lu)\n",
                        launched.process.instance_id.c_str(),
#ifdef _WIN32
                        launched.process.pid
#else
                        (unsigned long)launched.process.pid
#endif
            );
            return 0;
        } else if (action == std::string("stop")) {
            std::string id;
            for (int i = 3; i < argc; ++i) {
                parse_arg(argv[i], "--id", id);
            }
            if (id.empty()) {
                std::printf("stop requires --id\n");
                return 1;
            }
            if (!launcher_stop_instance(ctx, id)) {
                std::printf("instance not found: %s\n", id.c_str());
                return 1;
            }
            return 0;
        } else if (action == std::string("list")) {
            for (size_t i = 0; i < ctx.instances.size(); ++i) {
                const LauncherInstance &inst = ctx.instances[i];
                std::printf("%s | %s | pid=%lu | role=%s | display=%s\n",
                            inst.process.instance_id.c_str(),
                            inst.install_id.c_str(),
#ifdef _WIN32
                            inst.process.pid,
#else
                            (unsigned long)inst.process.pid,
#endif
                            inst.role.c_str(),
                            inst.display_mode.c_str());
            }
            if (ctx.instances.empty()) {
                std::printf("No running instances\n");
            }
            return 0;
        }
    }

    print_cli_usage();
    return 1;
}
