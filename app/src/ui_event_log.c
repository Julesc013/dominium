/*
UI event log helper implementation.
*/
#include "dominium/app/ui_event_log.h"

#include <string.h>

void dom_app_ui_event_log_init(dom_app_ui_event_log* log)
{
    if (!log) {
        return;
    }
    memset(log, 0, sizeof(*log));
}

int dom_app_ui_event_log_open(dom_app_ui_event_log* log, const char* path)
{
    if (!log) {
        return 0;
    }
    dom_app_ui_event_log_init(log);
    if (!path || !path[0]) {
        return 1;
    }
    log->handle = fopen(path, "w");
    if (!log->handle) {
        return 0;
    }
    log->enabled = 1;
    log->seq = 0u;
    return 1;
}

void dom_app_ui_event_log_close(dom_app_ui_event_log* log)
{
    if (!log) {
        return;
    }
    if (log->handle) {
        fclose(log->handle);
        log->handle = 0;
    }
    log->enabled = 0;
}

void dom_app_ui_event_log_emit(dom_app_ui_event_log* log,
                               const char* event_name,
                               const char* detail)
{
    if (!log || !log->enabled || !log->handle || !event_name || !event_name[0]) {
        return;
    }
    log->seq += 1u;
    fprintf(log->handle, "event_seq=%u event=%s",
            (unsigned int)log->seq,
            event_name);
    if (detail && detail[0]) {
        fprintf(log->handle, " %s", detail);
    }
    fputc('\n', log->handle);
    fflush(log->handle);
}
