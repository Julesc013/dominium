/*
FILE: source/domino/system/plat/cocoa/cocoa_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/cocoa/cocoa_sys
RESPONSIBILITY: Defines internal contract for `cocoa_sys`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_COCOA_SYS_H
#define DOMINO_COCOA_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>

#define COCOA_EVENT_QUEUE_SIZE 128

typedef struct dsys_window_t {
    void*            ns_window; /* actually NSWindow* */
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
} dsys_window;

typedef struct dsys_dir_iter_t {
    DIR* dir;
} dsys_dir_iter;

typedef struct dsys_process_t {
    int dummy;
} dsys_process;

typedef struct cocoa_global_t {
    int          initialized;
    dsys_window* main_window;
    dsys_event   queue[COCOA_EVENT_QUEUE_SIZE];
    int          head;
    int          tail;
} cocoa_global_t;

extern cocoa_global_t g_cocoa;

/* Objective-C bridge */
void   cocoa_objc_init_app(void);
void   cocoa_objc_shutdown(void);
void*  cocoa_objc_create_window(int width, int height, const char* title);
void   cocoa_objc_destroy_window(void* ns_window);
void   cocoa_objc_toggle_fullscreen(void* ns_window);
void   cocoa_objc_resize_window(void* ns_window, int w, int h);
void   cocoa_objc_get_window_size(void* ns_window, int* w, int* h);
void   cocoa_objc_pump_events(void);

bool cocoa_objc_get_path_exec(char* buf, size_t buf_size);
bool cocoa_objc_get_path_home(char* buf, size_t buf_size);
bool cocoa_objc_get_path_config(char* buf, size_t buf_size);
bool cocoa_objc_get_path_data(char* buf, size_t buf_size);
bool cocoa_objc_get_path_cache(char* buf, size_t buf_size);
bool cocoa_objc_get_path_temp(char* buf, size_t buf_size);

void cocoa_push_event(const dsys_event* ev);

const dsys_backend_vtable* dsys_cocoa_get_vtable(void);

#endif /* DOMINO_COCOA_SYS_H */
