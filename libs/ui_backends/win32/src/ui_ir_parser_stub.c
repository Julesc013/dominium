/*
FILE: shared_ui_win32/src/ui_ir_parser_stub.c
MODULE: Dominium
PURPOSE: UI IR parser stub (Win32).
NOTES: Stub only; deterministic placeholder.
*/
#include "dom_ui_win32/ui_win32.h"

int domui_win32_init(void)
{
    return 1;
}

int domui_win32_load_ui_ir(const char* path)
{
    (void)path;
    return 1;
}

int domui_win32_dispatch_command(const char* command_id, const char* args)
{
    (void)command_id;
    (void)args;
    return 0;
}
