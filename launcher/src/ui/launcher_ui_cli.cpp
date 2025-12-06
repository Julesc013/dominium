#include "launcher_ui_cli.h"
#include "launcher_context.h"
#include "launcher_db.h"
#include "launcher_discovery.h"
#include "launcher_process.h"
#include "launcher_plugins.h"
#include "launcher_logging.h"
#include "dom_shared/uuid.h"
#include "dom_shared/os_paths.h"

#include <cstdio>
#include <cstring>

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

static void print_usage()
{
    std::printf("dom_launcher CLI\n");
    std::printf("  installs list\n");
    std::printf("  installs add-path --path=PATH\n");
    std::printf("  instances list\n");
    std::printf("  instances start --install-id=ID [--role=client|server|tool] [--display=gui|tui|cli|none] [--universe=PATH]\n");
    std::printf("  instances stop --instance-id=ID\n");
    std::printf("  plugins list\n");
}

int launcher_run_cli(int argc, char **argv)
{
    LauncherContext ctx = init_launcher_context();
    db_load(ctx);
    launcher_plugins_load(ctx);

    if (argc < 2) {
        print_usage();
        return 0;
    }

    std::string group = argv[1];
    if (group == "installs") {
        if (argc < 3) { print_usage(); return 1; }
        std::string action = argv[2];
        if (action == "list") {
            std::vector<InstallInfo> installs = discover_installs(ctx);
            for (size_t i = 0; i < installs.size(); ++i) {
                std::printf("%s | %s | %s | %s\n",
                            installs[i].install_id.c_str(),
                            installs[i].install_type.c_str(),
                            installs[i].platform.c_str(),
                            installs[i].root_path.c_str());
                db_add_or_update_install(installs[i]);
            }
            db_save(ctx);
            return 0;
        } else if (action == "add-path") {
            std::string path;
            for (int i = 3; i < argc; ++i) {
                parse_arg(argv[i], "--path", path);
            }
            if (path.empty()) {
                std::printf("add-path requires --path\n");
                return 1;
            }
            db_add_manual_path(path);
            db_save(ctx);
            std::printf("added manual path: %s\n", path.c_str());
            return 0;
        }
    } else if (group == "instances") {
        if (argc < 3) { print_usage(); return 1; }
        std::string action = argv[2];
        if (action == "list") {
            std::vector<Instance> insts = list_instances();
            for (size_t i = 0; i < insts.size(); ++i) {
                std::printf("%s | %s | state=%s\n",
                            insts[i].instance_id.c_str(),
                            insts[i].install.install_id.c_str(),
                            insts[i].state.c_str());
            }
            if (insts.empty()) std::printf("no instances\n");
            return 0;
        } else if (action == "start") {
            std::string install_id;
            std::string role = "client";
            std::string display = "gui";
            std::string universe = "saves/default";
            for (int i = 3; i < argc; ++i) {
                parse_arg(argv[i], "--install-id", install_id);
                parse_arg(argv[i], "--role", role);
                parse_arg(argv[i], "--display", display);
                parse_arg(argv[i], "--universe", universe);
            }
            if (install_id.empty()) { std::printf("start requires --install-id\n"); return 1; }
            std::vector<InstallInfo> installs = discover_installs(ctx);
            InstallInfo *inst = find_install_by_id(installs, install_id);
            if (!inst) { std::printf("install not found\n"); return 1; }
            DomDisplayMode dm = DOM_DISPLAY_GUI;
            if (display == "cli") dm = DOM_DISPLAY_CLI;
            else if (display == "tui") dm = DOM_DISPLAY_TUI;
            else if (display == "none") dm = DOM_DISPLAY_NONE;
            Instance started = start_instance(ctx, *inst, role, dm, universe, "", "");
            std::printf("started instance %s\n", started.instance_id.c_str());
            return 0;
        } else if (action == "stop") {
            std::string iid;
            for (int i = 3; i < argc; ++i) parse_arg(argv[i], "--instance-id", iid);
            if (iid.empty()) { std::printf("stop requires --instance-id\n"); return 1; }
            if (!stop_instance(iid)) {
                std::printf("instance not found\n");
                return 1;
            }
            std::printf("stopped %s\n", iid.c_str());
            return 0;
        }
    } else if (group == "plugins") {
        std::string action = argc >= 3 ? argv[2] : "list";
        if (action == "list") {
            launcher_plugins_list();
            return 0;
        }
    }

    print_usage();
    return 1;
}
