/*
Stub launcher CLI entrypoint.
*/
#include <stdio.h>
#include <string.h>

#include "launcher/launcher.h"
#include "launcher/launcher_profile.h"

static void launcher_print_help(void)
{
    printf("usage: launcher [--help] [--version] <command>\n");
    printf("commands:\n");
    printf("  version         Show launcher version\n");
    printf("  list-profiles   List known profiles\n");
}

static void launcher_print_profiles(void)
{
    int count;
    int i;

    launcher_profile_load_all();
    count = launcher_profile_count();
    if (count <= 0) {
        printf("profiles: none\n");
        return;
    }

    for (i = 0; i < count; ++i) {
        const launcher_profile* p = launcher_profile_get(i);
        if (!p) {
            continue;
        }
        printf("%s\t%s\n", p->id, p->name);
    }
}

int main(int argc, char** argv)
{
    const char* cmd = 0;

    if (argc <= 1) {
        launcher_print_help();
        return 0;
    }

    cmd = argv[1];
    if (!cmd) {
        launcher_print_help();
        return 2;
    }

    if (strcmp(cmd, "--help") == 0 || strcmp(cmd, "-h") == 0) {
        launcher_print_help();
        return 0;
    }
    if (strcmp(cmd, "--version") == 0 || strcmp(cmd, "version") == 0) {
        printf("launcher 0.0.0\n");
        return 0;
    }
    if (strcmp(cmd, "list-profiles") == 0) {
        launcher_print_profiles();
        return 0;
    }

    printf("launcher: unknown command '%s'\n", cmd);
    launcher_print_help();
    return 2;
}
