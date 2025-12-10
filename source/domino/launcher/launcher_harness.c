#include "domino/launcher.h"

int main(int argc, char** argv)
{
    launcher_config cfg;
    (void)argc;
    (void)argv;

    launcher_config_load(&cfg);
    if (launcher_init(&cfg) != 0) {
        return 1;
    }
    launcher_run();
    launcher_shutdown();
    return 0;
}
