/*
UI event log helpers (deterministic, optional).
*/
#ifndef DOMINIUM_APP_UI_EVENT_LOG_H
#define DOMINIUM_APP_UI_EVENT_LOG_H

#include <stdio.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_app_ui_event_log {
    FILE* handle;
    uint32_t seq;
    int enabled;
} dom_app_ui_event_log;

void dom_app_ui_event_log_init(dom_app_ui_event_log* log);
int  dom_app_ui_event_log_open(dom_app_ui_event_log* log, const char* path);
void dom_app_ui_event_log_close(dom_app_ui_event_log* log);
void dom_app_ui_event_log_emit(dom_app_ui_event_log* log,
                               const char* event_name,
                               const char* detail);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_UI_EVENT_LOG_H */
