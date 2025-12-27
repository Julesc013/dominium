/*
FILE: source/dominium/setup/installers/windows/exe/common/src/capability.c
MODULE: Dominium Setup EXE
PURPOSE: OS capability detection for Windows installer variants.
*/
#include "dsu_exe_capability.h"

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif
#include <string.h>

void dsu_exe_detect_capabilities(dsu_exe_capabilities_t *out_caps) {
    dsu_exe_capabilities_t caps;
    memset(&caps, 0, sizeof(caps));

#if defined(_WIN32)
    {
        OSVERSIONINFOEXA os;
        memset(&os, 0, sizeof(os));
        os.dwOSVersionInfoSize = sizeof(os);
        if (GetVersionExA((OSVERSIONINFOA *)&os)) {
            if (os.dwPlatformId == VER_PLATFORM_WIN32_NT) {
                caps.is_nt = 1;
            } else if (os.dwPlatformId == VER_PLATFORM_WIN32_WINDOWS) {
                caps.is_win9x = 1;
            }
        } else {
            DWORD v = GetVersion();
            if ((v & 0x80000000u) == 0u) {
                caps.is_nt = 1;
            } else {
                caps.is_win9x = 1;
            }
        }
    }
    {
        DWORD pids[4];
        DWORD count = GetConsoleProcessList(pids, (DWORD)(sizeof(pids) / sizeof(pids[0])));
        if (count > 1u) {
            caps.has_console = 1;
        } else {
            HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
            DWORD mode = 0u;
            if (hOut != INVALID_HANDLE_VALUE && GetConsoleMode(hOut, &mode)) {
                caps.has_console = 1;
            }
        }
    }
#endif

    if (out_caps) {
        *out_caps = caps;
    }
}
