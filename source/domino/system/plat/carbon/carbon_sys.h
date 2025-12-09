#ifndef DOMINO_CARBON_SYS_H
#define DOMINO_CARBON_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <Carbon/Carbon.h>
#include <dirent.h>

struct dsys_window_t {
    WindowRef        window_ref;
    int32_t          width;
    int32_t          height;
    int32_t          last_x;
    int32_t          last_y;
    dsys_window_mode mode;
};

struct dsys_dir_iter_t {
    DIR*  dir;
    char  base[260];
};

struct dsys_process_t {
    int dummy;
};

typedef struct carbon_global_t {
    int            initialized;
    WindowRef      main_window;
    EventHandlerUPP app_event_upp;
    EventHandlerUPP win_event_upp;
    EventHandlerRef app_event_ref;
    EventHandlerRef win_event_ref;
    dsys_event     event_queue[64];
    int            event_head;
    int            event_tail;
} carbon_global_t;

extern carbon_global_t g_carbon;

const dsys_backend_vtable* dsys_carbon_get_vtable(void);

#endif /* DOMINO_CARBON_SYS_H */
