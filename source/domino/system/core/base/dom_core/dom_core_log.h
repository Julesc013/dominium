#ifndef DOM_CORE_LOG_H
#define DOM_CORE_LOG_H

#include "dom_core_types.h"

typedef enum DomLogLevel {
    DOM_LOG_DEBUG = 0,
    DOM_LOG_INFO,
    DOM_LOG_WARN,
    DOM_LOG_ERROR,
    DOM_LOG_FATAL
} DomLogLevel;

typedef void (*DomLogSinkFn)(DomLogLevel level,
                             const char *file,
                             int line,
                             const char *msg,
                             void *user_data);

void dom_log_init(DomLogSinkFn sink, void *user_data);
void dom_log_shutdown(void);
void dom_log_message(DomLogLevel level, const char *file, int line, const char *fmt, ...);

#define DOM_LOG_DEBUG(msg) dom_log_message(DOM_LOG_DEBUG, __FILE__, __LINE__, msg)
#define DOM_LOG_INFO(msg)  dom_log_message(DOM_LOG_INFO,  __FILE__, __LINE__, msg)
#define DOM_LOG_WARN(msg)  dom_log_message(DOM_LOG_WARN,  __FILE__, __LINE__, msg)
#define DOM_LOG_ERROR(msg) dom_log_message(DOM_LOG_ERROR, __FILE__, __LINE__, msg)
#define DOM_LOG_FATAL(msg) dom_log_message(DOM_LOG_FATAL, __FILE__, __LINE__, msg)

#endif /* DOM_CORE_LOG_H */
