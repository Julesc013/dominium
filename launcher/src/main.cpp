#include "launcher_ui_cli.h"
#include "launcher_ui_tui.h"
#include "launcher_ui_gui.h"
#include <cstring>

int main(int argc, char **argv)
{
    bool want_gui = true;
    bool want_tui = false;
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--cli") == 0) want_gui = false;
        if (std::strcmp(argv[i], "--tui") == 0) { want_gui = false; want_tui = true; }
        if (std::strcmp(argv[i], "--gui") == 0) { want_gui = true; want_tui = false; }
    }
    if (want_gui) {
        int rc = launcher_run_gui(argc, argv);
        if (rc == 0) return 0;
    }
    if (want_tui) {
        int rc = launcher_run_tui(argc, argv);
        if (rc == 0) return 0;
    }
    return launcher_run_cli(argc, argv);
}
