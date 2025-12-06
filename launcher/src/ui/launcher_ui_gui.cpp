#include "dom_launcher/launcher_ui_gui.h"
#include <cstdio>

namespace dom_launcher {

int launcher_run_gui(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    std::printf("GUI not implemented; falling back to CLI\n");
    return 1;
}

} // namespace dom_launcher
