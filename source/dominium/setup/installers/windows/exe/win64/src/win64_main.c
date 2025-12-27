/*
FILE: source/dominium/setup/installers/windows/exe/win64/src/win64_main.c
MODULE: Dominium Setup EXE (Win64)
PURPOSE: Win64 entry wrapper (shared implementation in win32_entry).
*/
#include "dsu_exe_win32.h"

int main(int argc, char **argv) {
    return dsu_exe_entry_run(argc, argv, "win64-x64", "exe-win64");
}
