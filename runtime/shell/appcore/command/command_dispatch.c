/*
FILE: libs/appcore/command/command_dispatch.c
MODULE: Dominium
PURPOSE: Command dispatch stub (no behavior; UI must call this path).
NOTES: Implementations must be deterministic and use explicit command registry.
*/
#include "command_registry.h"

int appcore_dispatch_command(const dom_app_command_desc* cmd)
{
    (void)cmd;
    /* TODO: route to application-specific command handlers. */
    return -1;
}
