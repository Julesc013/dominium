#include "domino/system/dsys.h"

#include <windows.h>

int dsys_running_in_terminal(void)
{
    /* If there is a console window, treat as terminal. */
    HWND hwnd = GetConsoleWindow();
    if (hwnd != NULL) {
        return 1;
    }

    /* Fallback: check if STD_OUTPUT_HANDLE is a console. */
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD mode;
    if (hOut != INVALID_HANDLE_VALUE && GetConsoleMode(hOut, &mode)) {
        return 1;
    }

    return 0;
}
