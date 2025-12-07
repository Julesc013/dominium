#ifndef DOMINIUM_DOM_CORE_H
#define DOMINIUM_DOM_CORE_H

/* Small public-facing core surface. Keep C89 friendly. */

#include <stddef.h>
#include <stdint.h>

typedef int32_t  dom_i32;
typedef uint32_t dom_u32;
typedef int64_t  dom_i64;
typedef uint64_t dom_u64;
typedef uint8_t  dom_bool8;

enum dom_log_level {
    DOM_LOG_DEBUG = 0,
    DOM_LOG_INFO  = 1,
    DOM_LOG_WARN  = 2,
    DOM_LOG_ERROR = 3
};

void dom_log(enum dom_log_level lvl, const char* category, const char* msg);

#endif /* DOMINIUM_DOM_CORE_H */
