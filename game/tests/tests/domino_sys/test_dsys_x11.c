/*
FILE: tests/domino_sys/test_dsys_x11.c
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
    dsys_window_desc wdesc;
    dsys_window*     win;
    dsys_event       ev;
    char             path[260];
    dsys_process*    proc;
    dsys_process_desc pdesc;
    const char*      args[2];
    int32_t          w;
    int32_t          h;
    int              exit_code;
    int              result;
    int              i;

    result = 0;
    if (dsys_init() != DSYS_OK) {
        printf("x11: dsys_init failed\n");
        return 1;
    }

    (void)dsys_get_caps();
    (void)dsys_time_now_us();
    dsys_sleep_ms(1u);

    wdesc.x = 0;
    wdesc.y = 0;
    wdesc.width = 320;
    wdesc.height = 240;
    wdesc.mode = DWIN_MODE_WINDOWED;

    win = dsys_window_create(&wdesc);
    if (win) {
        dsys_window_get_size(win, &w, &h);
        dsys_window_set_size(win, w + 10, h + 10);
        dsys_window_get_size(win, &w, &h);
        (void)dsys_window_get_native_handle(win);
    }

    for (i = 0; i < 4; ++i) {
        if (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                break;
            }
        }
        dsys_sleep_ms(10u);
    }

    if (!dsys_get_path(DSYS_PATH_APP_ROOT, path, sizeof(path))) {
        printf("x11: DSYS_PATH_APP_ROOT unavailable\n");
        result = 1;
    }
    if (!dsys_get_path(DSYS_PATH_USER_DATA, path, sizeof(path))) {
        printf("x11: DSYS_PATH_USER_DATA unavailable\n");
        result = 1;
    }
    if (!dsys_get_path(DSYS_PATH_TEMP, path, sizeof(path))) {
        printf("x11: DSYS_PATH_TEMP unavailable\n");
        result = 1;
    }

    args[0] = "/bin/true";
    args[1] = NULL;
    pdesc.exe = "/bin/true";
    pdesc.argv = args;
    pdesc.flags = 0;
    proc = dsys_process_spawn(&pdesc);
    if (proc) {
        exit_code = dsys_process_wait(proc);
        if (exit_code != 0) {
            printf("x11: spawned process exit code %d\n", exit_code);
            result = 1;
        }
        dsys_process_destroy(proc);
    }

    if (win) {
        dsys_window_destroy(win);
    }
    dsys_shutdown();
    return result;
}
