#include "dom_launcher/launcher_ui_cli.h"
#include "dom_launcher/launcher_state.h"
#include "dom_launcher/launcher_discovery.h"
#include "dom_shared/logging.h"

#include <cstdio>
#include <cstring>

namespace dom_launcher {

static void print_banner()
{
    std::printf("Dominium Launcher (CLI stub)\n");
    std::printf("Commands:\n");
    std::printf("  list      - list installs\n");
    std::printf("  refresh   - rescan default roots and manual paths\n");
    std::printf("  exit/quit - leave launcher\n");
    std::printf("\n");
}

static void print_installs(const LauncherState& state)
{
    if (state.installs.empty()) {
        std::printf("No installs discovered.\n");
        return;
    }
    for (size_t i = 0; i < state.installs.size(); ++i) {
        const dom_shared::InstallInfo& ii = state.installs[i];
        std::printf("[%d] %s | %s | %s | %s\n",
                    (int)i,
                    ii.install_id.c_str(),
                    ii.install_type.c_str(),
                    ii.version.c_str(),
                    ii.root_path.c_str());
    }
}

int launcher_run_cli(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    LauncherState& state = get_state();
    print_banner();
    print_installs(state);
    char line[256];
    for (;;) {
        std::printf("> ");
        if (!std::fgets(line, sizeof(line), stdin)) {
            break;
        }
        // trim newline
        size_t len = std::strlen(line);
        if (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
            line[len - 1] = '\0';
        }
        if (std::strcmp(line, "exit") == 0 || std::strcmp(line, "quit") == 0) {
            break;
        } else if (std::strcmp(line, "list") == 0) {
            print_installs(state);
        } else if (std::strcmp(line, "refresh") == 0) {
            std::vector<dom_shared::InstallInfo> discovered = discover_installs(state);
            merge_discovered_installs(state, discovered);
            state_save();
            dom_shared::log_info("Refreshed installs. Found %d.", (int)state.installs.size());
            print_installs(state);
        } else if (std::strlen(line) == 0) {
            continue;
        } else {
            std::printf("Unknown command: %s\n", line);
        }
    }
    return 0;
}

} // namespace dom_launcher
