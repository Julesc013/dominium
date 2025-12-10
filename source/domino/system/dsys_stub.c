#include "domino/system/dsys.h"

#include <string.h>

static dsys_log_fn g_dsys_log = 0;

void dsys_set_log_callback(dsys_log_fn fn) {
    g_dsys_log = fn;
}

static void dsys_log(const char* message) {
    if (g_dsys_log) {
        g_dsys_log(message);
    }
}

dsys_result dsys_init(void) {
    dsys_log("dsys_init: stub backend");
    return DSYS_OK;
}

void dsys_shutdown(void) {
    dsys_log("dsys_shutdown: stub backend");
}

int dsys_input_poll_raw(dsys_input_event* ev) {
    int key;
    key = dsys_terminal_poll_key();
    if (key != 0) {
        if (ev) {
            memset(ev, 0, sizeof(*ev));
            ev->type = DSYS_INPUT_EVENT_KEY_DOWN;
            ev->payload.key.keycode = (i32)key;
            ev->payload.key.repeat = 0;
            ev->payload.key.translated = (key >= 32 && key <= 126) ? key : 0;
        }
        return 1;
    }
    if (ev) {
        memset(ev, 0, sizeof(*ev));
        ev->type = DSYS_INPUT_EVENT_NONE;
    }
    return 0;
}

void dsys_ime_start(void) {
}

void dsys_ime_stop(void) {
}

void dsys_ime_set_cursor(int32_t x, int32_t y) {
    (void)x;
    (void)y;
}

int dsys_ime_poll(dsys_ime_event* ev) {
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }
    return 0;
}
