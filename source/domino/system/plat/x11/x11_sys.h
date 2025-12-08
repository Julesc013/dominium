#ifndef DOMINO_X11_SYS_H
#define DOMINO_X11_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <dirent.h>
#include <sys/types.h>
#include <unistd.h>

typedef struct x11_global_t {
    Display* display;
    int      screen;
    Atom     wm_delete_window;
    Atom     net_wm_state;
    Atom     net_wm_state_fullscreen;
} x11_global_t;

struct dsys_window_t {
    Display*         display;
    int              screen;
    Window           window;
    Atom             wm_delete_window;
    Atom             net_wm_state;
    Atom             net_wm_state_fullscreen;
    int32_t          width;
    int32_t          height;
    int32_t          last_x;
    int32_t          last_y;
    dsys_window_mode mode;
    struct dsys_window_t* next;
};

struct dsys_dir_iter_t {
    DIR*  dir;
    char  base[260];
};

struct dsys_process_t {
    pid_t pid;
};

const dsys_backend_vtable* dsys_x11_get_vtable(void);

#endif /* DOMINO_X11_SYS_H */
