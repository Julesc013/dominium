/*
Win32 server status UI shell (stub).
*/
#if defined(_WIN32)
#include <windows.h>
#endif

#include "dom_ui_win32/ui_win32.h"
#include "command/command_registry.h"

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE prev, PWSTR cmdline, int show)
{
    const dom_app_command_desc* cmd;
    (void)inst;
    (void)prev;
    (void)cmdline;
    (void)show;

    domui_win32_init();
    domui_win32_register_accessibility();
    domui_win32_enable_keyboard_nav(1);
    domui_win32_set_dpi_scale(96u);
    domui_win32_load_ui_ir("server/ui");

    cmd = appcore_command_find("version");
    (void)appcore_dispatch_command(cmd);

    return domui_win32_run_shell(L"Dominium Server");
}
