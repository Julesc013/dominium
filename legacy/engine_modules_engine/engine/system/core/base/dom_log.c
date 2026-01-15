/*
FILE: source/domino/system/core/base/dom_log.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_log
RESPONSIBILITY: Implements `dom_log`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/dom_core.h"

#include <stdio.h>

void dom_log(enum dom_log_level lvl, const char* category, const char* msg)
{
    const char* lvl_str = "INFO";
    switch (lvl) {
    case DOM_LOG_DEBUG: lvl_str = "DEBUG"; break;
    case DOM_LOG_INFO:  lvl_str = "INFO"; break;
    case DOM_LOG_WARN:  lvl_str = "WARN"; break;
    case DOM_LOG_ERROR: lvl_str = "ERROR"; break;
    default: break;
    }
    if (!category) category = "core";
    if (!msg) msg = "";
    printf("[%s] %s: %s\n", lvl_str, category, msg);
}
