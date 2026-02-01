/*
FILE: tests/domino_sys/test_dsys_stub.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_sys
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/sys.h"

#include <stdio.h>

int main(void)
{
    dsys_caps caps;
    dsys_window_desc wdesc;
    dsys_window* win;
    char path[8];
    dsys_event ev;
    int32_t w;
    int32_t h;

    if (dsys_init() != DSYS_OK) {
        printf("dsys_init failed\n");
        return 1;
    }

    caps = dsys_get_caps();
    (void)caps;

    (void)dsys_time_now_us();
    dsys_sleep_ms(1u);

    wdesc.x = 0;
    wdesc.y = 0;
    wdesc.width = 320;
    wdesc.height = 240;
    wdesc.mode = DWIN_MODE_WINDOWED;

    win = dsys_window_create(&wdesc);
    if (win) {
        dsys_window_set_size(win, 640, 360);
        dsys_window_get_size(win, &w, &h);
        (void)w;
        (void)h;
        dsys_window_set_mode(win, DWIN_MODE_BORDERLESS);
        (void)dsys_window_get_native_handle(win);
        dsys_window_destroy(win);
    }

    dsys_poll_event(&ev);

    if (!dsys_get_path(DSYS_PATH_APP_ROOT, path, sizeof(path))) {
        dsys_shutdown();
        return 1;
    }

    dsys_shutdown();
    return 0;
}
