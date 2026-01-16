/*
Stub setup GUI entrypoint.
*/
#include <stdio.h>

#include "dsu/dsu_frontend.h"

int dsu_gui_run(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    printf("setup gui stub\\n");
    return 0;
}

int main(int argc, char** argv)
{
    return dsu_gui_run(argc, argv);
}
