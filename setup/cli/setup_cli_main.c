/*
Stub setup CLI entrypoint.
*/
#include <stdio.h>
#include <string.h>

#include "dsk/dsk_setup.h"

static void setup_print_help(void)
{
    printf("usage: setup [--help] [--version] <command>\\n");
    printf("commands:\\n");
    printf("  version   Show setup version\\n");
    printf("  status    Show setup status\\n");
}

int main(int argc, char** argv)
{
    const char* cmd = 0;

    if (argc <= 1) {
        setup_print_help();
        return 0;
    }

    cmd = argv[1];
    if (!cmd) {
        setup_print_help();
        return 2;
    }

    if (strcmp(cmd, "--help") == 0 || strcmp(cmd, "-h") == 0) {
        setup_print_help();
        return 0;
    }
    if (strcmp(cmd, "--version") == 0 || strcmp(cmd, "version") == 0) {
        printf("setup %s\\n", dsk_setup_version());
        return 0;
    }
    if (strcmp(cmd, "status") == 0) {
        printf("setup status: ok (stub)\\n");
        return dsk_setup_status();
    }

    printf("setup: unknown command '%s'\\n", cmd);
    setup_print_help();
    return 2;
}
