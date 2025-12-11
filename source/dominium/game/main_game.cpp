#include "domino/system/dsys.h"
#include "domino/app/startup.h"

int main(int argc, char** argv) {
    d_app_params p;
    p.argc = argc;
    p.argv = argv;
    p.has_terminal = dsys_running_in_terminal();
    p.mode = d_app_parse_mode(argc, argv);

    return d_app_run_game(&p);
}
