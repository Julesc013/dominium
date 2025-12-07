#include <stddef.h>

#include "dominium/launch_api.h"

int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    /* Later: parse args for specific view/instance actions. */
    return dominium_launcher_run(NULL);
}
