#include <cstring>
#include <string>

// Forward declarations for UI entrypoints.
int launcher_run_cli(int argc, char **argv);
int launcher_run_tui(int argc, char **argv);
int launcher_run_gui(int argc, char **argv);

int main(int argc, char **argv)
{
    bool want_gui = false;
    bool want_tui = false;
    int i;
    for (i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--gui") == 0) want_gui = true;
        if (std::strcmp(argv[i], "--tui") == 0) want_tui = true;
        if (std::strcmp(argv[i], "--cli") == 0) { want_gui = false; want_tui = false; }
    }
    if (want_gui) {
        return launcher_run_gui(argc, argv);
    }
    if (want_tui) {
        return launcher_run_tui(argc, argv);
    }
    return launcher_run_cli(argc, argv);
}
