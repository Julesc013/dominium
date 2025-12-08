#include "domino/sys.h"

#include <stdio.h>
#include <string.h>

int main(void)
{
    dsys_caps        caps;
    dsys_event       ev;
    dsys_window*     win;
    char             path[260];
    char             file_path[520];
    const char*      payload;
    size_t           wrote;
    size_t           read;
    char             buffer[16];
    void*            fh;
    dsys_process*    proc;
    dsys_process_desc pdesc;
    const char*      args[2];
    int              exit_code;
    int              result;

    result = 0;
    if (dsys_init() != DSYS_OK) {
        printf("posix: dsys_init failed\n");
        return 1;
    }

    caps = dsys_get_caps();
    if (caps.has_windows) {
        printf("posix: caps.has_windows should be false\n");
        result = 1;
    }

    (void)dsys_time_now_us();
    dsys_sleep_ms(1u);

    win = dsys_window_create(NULL);
    if (win != NULL) {
        printf("posix: window_create expected NULL\n");
        dsys_window_destroy(win);
        result = 1;
    }

    if (dsys_poll_event(&ev)) {
        printf("posix: poll_event should return false\n");
        result = 1;
    }

    if (!dsys_get_path(DSYS_PATH_APP_ROOT, path, sizeof(path)) || path[0] == '\0') {
        printf("posix: DSYS_PATH_APP_ROOT unavailable\n");
        result = 1;
    }
    if (!dsys_get_path(DSYS_PATH_USER_DATA, path, sizeof(path)) || path[0] == '\0') {
        printf("posix: DSYS_PATH_USER_DATA unavailable\n");
        result = 1;
    }
    if (!dsys_get_path(DSYS_PATH_USER_CONFIG, path, sizeof(path)) || path[0] == '\0') {
        printf("posix: DSYS_PATH_USER_CONFIG unavailable\n");
        result = 1;
    }
    if (!dsys_get_path(DSYS_PATH_USER_CACHE, path, sizeof(path)) || path[0] == '\0') {
        printf("posix: DSYS_PATH_USER_CACHE unavailable\n");
        result = 1;
    }

    if (dsys_get_path(DSYS_PATH_TEMP, path, sizeof(path)) && path[0] != '\0') {
        file_path[0] = '\0';
        strncpy(file_path, path, sizeof(file_path) - 1u);
        file_path[sizeof(file_path) - 1u] = '\0';
        if (strlen(file_path) + 2u < sizeof(file_path) && file_path[strlen(file_path) - 1u] != '/') {
            strncat(file_path, "/", sizeof(file_path) - strlen(file_path) - 1u);
        }
        strncat(file_path, "dsys_posix_test.tmp", sizeof(file_path) - strlen(file_path) - 1u);

        fh = dsys_file_open(file_path, "wb");
        payload = "ok";
        if (fh) {
            wrote = dsys_file_write(fh, payload, strlen(payload));
            dsys_file_close(fh);
            if (wrote != strlen(payload)) {
                printf("posix: file_write short write\n");
                result = 1;
            }
        }

        fh = dsys_file_open(file_path, "rb");
        if (fh) {
            memset(buffer, 0, sizeof(buffer));
            read = dsys_file_read(fh, buffer, sizeof(buffer) - 1u);
            dsys_file_close(fh);
            if (read == 0u || strcmp(buffer, payload) != 0) {
                printf("posix: file_read mismatch\n");
                result = 1;
            }
        }
        remove(file_path);
    } else {
        printf("posix: DSYS_PATH_TEMP unavailable\n");
        result = 1;
    }

    if (dsys_get_path(DSYS_PATH_TEMP, path, sizeof(path)) && path[0] != '\0') {
        dsys_dir_iter* it;
        dsys_dir_entry entry;
        it = dsys_dir_open(path);
        if (it) {
            (void)dsys_dir_next(it, &entry);
            dsys_dir_close(it);
        } else {
            printf("posix: dir_open failed\n");
            result = 1;
        }
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
            printf("posix: spawned process exit code %d\n", exit_code);
            result = 1;
        }
        dsys_process_destroy(proc);
    }

    dsys_shutdown();
    return result;
}
