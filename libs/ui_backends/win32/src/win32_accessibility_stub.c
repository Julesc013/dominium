/*
FILE: shared_ui_win32/src/win32_accessibility_stub.c
MODULE: Dominium
PURPOSE: Win32 accessibility mapping hooks (stub).
NOTES: No business logic; presentation only.
*/
#include "dom_ui_win32/ui_win32.h"

void domui_win32_register_accessibility(void)
{
}

void domui_win32_enable_keyboard_nav(int enabled)
{
    (void)enabled;
}
