#include "domino/system/dsys.h"
#include "dsys_internal.h"

#include <stdlib.h>
#include <string.h>

dsys_window* dsys_window_create(const dsys_window_desc* desc) {
    dsys_window* win;
    dsys_window_desc local;

    if (desc) {
        local = *desc;
    } else {
        local.x = 0;
        local.y = 0;
        local.width = 0;
        local.height = 0;
        local.mode = DWIN_MODE_WINDOWED;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->width = local.width;
    win->height = local.height;
    win->mode = local.mode;
    return win;
}

void dsys_window_destroy(dsys_window* win) {
    if (!win) {
        return;
    }
    free(win);
}

int dsys_window_should_close(dsys_window* win) {
    (void)win;
    return 1;
}

void dsys_window_present(dsys_window* win) {
    (void)win;
}

void dsys_window_get_size(dsys_window* win, int32_t* out_w, int32_t* out_h) {
    if (!win) {
        if (out_w) *out_w = 0;
        if (out_h) *out_h = 0;
        return;
    }
    if (out_w) *out_w = win->width;
    if (out_h) *out_h = win->height;
}
