#include "domino/system/dsys.h"

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
