#ifndef DOMINO_CARBON_SYS_H
#define DOMINO_CARBON_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <Carbon/Carbon.h>
#include <dirent.h>

#define CARBON_EVENT_QUEUE_SIZE 64

struct dsys_window_t {
    WindowRef        window;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
};

struct dsys_dir_iter_t {
    DIR* dir;
};

struct dsys_process_t {
    FSRef dummy_ref;
};

typedef struct carbon_global_t {
    int           initialized;
    dsys_window*  main_window;
    dsys_event    queue[CARBON_EVENT_QUEUE_SIZE];
    int           q_head;
    int           q_tail;
    uint64_t      time_base_us;
    int32_t       last_mouse_x;
    int32_t       last_mouse_y;
    int           mouse_pos_valid;
} carbon_global_t;

extern carbon_global_t g_carbon;

const dsys_backend_vtable* dsys_carbon_get_vtable(void);

#endif /* DOMINO_CARBON_SYS_H */
