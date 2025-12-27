/*
FILE: source/dominium/setup/installers/windows/exe/win32/src/win32_main.c
MODULE: Dominium Setup EXE (Win32)
PURPOSE: Win32 entry wrapper.
*/
#include "dsu_exe_win32.h"

int main(int argc, char **argv) {
    return dsu_exe_entry_run(argc, argv, "win32-x86", "exe-win32");
}
