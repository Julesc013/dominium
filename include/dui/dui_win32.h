/*
FILE: include/dui/dui_win32.h
MODULE: DUI
RESPONSIBILITY: Win32 backend helpers for batching and debug counters.
*/
#ifndef DUI_WIN32_H_INCLUDED
#define DUI_WIN32_H_INCLUDED

#if defined(_WIN32)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif

void dui_win32_begin_batch(HWND parent);
void dui_win32_end_batch(HWND parent);

#if defined(DUI_WIN32_DEBUG_COUNTERS)
void dui_win32_debug_dump_counters(void);
#else
static void dui_win32_debug_dump_counters(void) { }
#endif

#ifdef __cplusplus
} /* extern "C" */
#endif

#else
#define dui_win32_begin_batch(parent) ((void)(parent))
#define dui_win32_end_batch(parent) ((void)(parent))
#define dui_win32_debug_dump_counters() ((void)0)
#endif

#endif /* DUI_WIN32_H_INCLUDED */
