/*
FILE: include/dominium/dom_core.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_core
RESPONSIBILITY: Defines the public contract for `dom_core` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
