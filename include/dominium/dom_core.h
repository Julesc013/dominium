#ifndef DOMINIUM_DOM_CORE_H
#define DOMINIUM_DOM_CORE_H

/* Small public-facing core surface. Keep C89 friendly. */

#include <stddef.h>
#include <stdint.h>
#include "domino/sys.h"

typedef int32_t  dom_i32;
typedef uint32_t dom_u32;
typedef int64_t  dom_i64;
typedef uint64_t dom_u64;
typedef uint8_t  dom_bool8;

/* Legacy aliasing to the new dm_sys_* surface. */
enum dom_log_level {
    DOM_LOG_DEBUG = DM_SYS_LOG_DEBUG,
    DOM_LOG_INFO  = DM_SYS_LOG_INFO,
    DOM_LOG_WARN  = DM_SYS_LOG_WARN,
    DOM_LOG_ERROR = DM_SYS_LOG_ERROR
};

static inline void dom_log(enum dom_log_level lvl, const char* category, const char* msg)
{
    dm_sys_log((enum dm_sys_log_level)lvl, category, msg);
}

#endif /* DOMINIUM_DOM_CORE_H */
