#ifndef DOMINIUM_DOM_CORE_H
#define DOMINIUM_DOM_CORE_H

/* Small public-facing core surface. Keep C89 friendly. */

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/sys.h"

typedef int32_t  dom_i32;
typedef uint32_t dom_u32;
typedef int64_t  dom_i64;
typedef uint64_t dom_u64;
typedef uint8_t  dom_bool8;

enum dom_log_level {
    DOM_LOG_DEBUG = DOMINO_LOG_DEBUG,
    DOM_LOG_INFO  = DOMINO_LOG_INFO,
    DOM_LOG_WARN  = DOMINO_LOG_WARN,
    DOM_LOG_ERROR = DOMINO_LOG_ERROR
};

static void dom_log(enum dom_log_level lvl, const char* category, const char* msg)
{
    domino_sys_log(NULL, (domino_log_level)lvl, category, msg);
}

#endif /* DOMINIUM_DOM_CORE_H */
