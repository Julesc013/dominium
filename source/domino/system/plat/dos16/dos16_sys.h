#ifndef DOMINO_DOS16_SYS_H
#define DOMINO_DOS16_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>

/* Framebuffer descriptor for real-mode DOS */
struct dos16_fb_handle {
    void _far* base;      /* e.g., 0xA000:0 */
    unsigned short width;
    unsigned short height;
    unsigned short pitch;
    unsigned char  bpp;
    unsigned char  is_vesa;
    unsigned short vesa_mode;
};

struct dsys_window_t {
    struct dos16_fb_handle fb;
    dsys_window_mode       mode;
};

struct dsys_process_t {
    int dummy;
};

struct dsys_dir_iter_t {
    DIR* dir;
};

typedef struct dos16_global_t {
    int           initialized;
    dsys_window*  main_window;

    int           mouse_present;
    int16_t       mouse_x;
    int16_t       mouse_y;
    unsigned int  mouse_buttons;

    dsys_event    event_queue[32];
    int           ev_head;
    int           ev_tail;
} dos16_global_t;

extern dos16_global_t g_dos16;

const dsys_backend_vtable* dsys_dos16_get_vtable(void);

#endif /* DOMINO_DOS16_SYS_H */
