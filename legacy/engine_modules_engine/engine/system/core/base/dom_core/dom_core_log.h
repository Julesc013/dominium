/*
FILE: source/domino/system/core/base/dom_core/dom_core_log.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_log
RESPONSIBILITY: Defines internal contract for `dom_core_log`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
