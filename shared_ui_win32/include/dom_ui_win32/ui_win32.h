/*
FILE: shared_ui_win32/include/dom_ui_win32/ui_win32.h
MODULE: Dominium
PURPOSE: Win32 UI rendering stubs for app shells.
NOTES: Pure presentation; no business logic; deterministic inputs only.
*/
#ifndef DOMINIUM_UI_WIN32_H
#define DOMINIUM_UI_WIN32_H

#include <wchar.h>
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

int domui_win32_init(void);
int domui_win32_load_ui_ir(const char* path);
int domui_win32_dispatch_command(const char* command_id, const char* args);
int domui_win32_run_shell(const wchar_t* title);

/* Accessibility + input stubs. */
void domui_win32_register_accessibility(void);
void domui_win32_enable_keyboard_nav(int enabled);
void domui_win32_set_dpi_scale(u32 dpi);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_UI_WIN32_H */
