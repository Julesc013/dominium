#ifndef DOMINO_COCOA_SYS_H
#define DOMINO_COCOA_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>
#include <sys/types.h>

struct dsys_window_t {
    void*                  native_handle; /* NSWindow* */
    void*                  objc_ref;      /* DominoWindow* retained on the ObjC side */
    int32_t                width;
    int32_t                height;
    int32_t                last_x;
    int32_t                last_y;
    dsys_window_mode       mode;
    struct dsys_window_t*  next;
};

struct dsys_dir_iter_t {
    DIR*  dir;
    char  base[260];
};

struct dsys_process_t {
    pid_t pid;
};

const dsys_backend_vtable* dsys_cocoa_get_vtable(void);

/* Objective-C bridge (implemented in cocoa_win.m) */
dsys_result cocoa_app_init(void);
void        cocoa_app_shutdown(void);

dsys_window* cocoa_win_create(const dsys_window_desc* desc);
void         cocoa_win_destroy(dsys_window* win);
void         cocoa_win_set_mode(dsys_window* win, dsys_window_mode mode);
void         cocoa_win_set_size(dsys_window* win, int32_t w, int32_t h);
void         cocoa_win_get_size(dsys_window* win, int32_t* w, int32_t* h);
void*        cocoa_win_get_native_handle(dsys_window* win);

bool cocoa_win_poll_event(dsys_event* ev);

#endif /* DOMINO_COCOA_SYS_H */
