/*
FILE: source/domino/system/core/base/dom_core/dom_core_err.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_err
RESPONSIBILITY: Implements `dom_core_err`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_core_err.h"

const char *dom_err_str(dom_err_t code)
{
    switch (code) {
    case DOM_OK:                 return "OK";
    case DOM_ERR_UNKNOWN:        return "UNKNOWN";
    case DOM_ERR_INVALID_ARG:    return "INVALID_ARG";
    case DOM_ERR_OUT_OF_MEMORY:  return "OUT_OF_MEMORY";
    case DOM_ERR_OVERFLOW:       return "OVERFLOW";
    case DOM_ERR_UNDERFLOW:      return "UNDERFLOW";
    case DOM_ERR_BOUNDS:         return "BOUNDS";
    case DOM_ERR_NOT_FOUND:      return "NOT_FOUND";
    case DOM_ERR_NOT_IMPLEMENTED:return "NOT_IMPLEMENTED";
    case DOM_ERR_IO:             return "IO";
    default:                     return "UNSPECIFIED";
    }
}
