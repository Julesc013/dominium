/*
Stub setup TUI entrypoint.
*/
#include <stdio.h>

#include "dsu/dsu_frontend.h"

int dsu_tui_run(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    printf("setup tui stub\\n");
    return 0;
}

int main(int argc, char** argv)
{
    return dsu_tui_run(argc, argv);
}
