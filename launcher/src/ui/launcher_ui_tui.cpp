#include "dom_launcher/launcher_ui_tui.h"
#include <cstdio>

namespace dom_launcher {

int launcher_run_tui(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    std::printf("TUI not implemented; use --cli\n");
    return 1;
}

} // namespace dom_launcher
