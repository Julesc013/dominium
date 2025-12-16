/*
FILE: source/domino/system/dsys_terminal_detect_winnt.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_terminal_detect_winnt
RESPONSIBILITY: Implements `dsys_terminal_detect_winnt`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
