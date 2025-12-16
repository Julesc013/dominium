/*
FILE: source/domino/system/core/base/dom_core/dom_core_err.h
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
#ifndef DOM_CORE_ERR_H
#define DOM_CORE_ERR_H

#include "dom_core_types.h"

enum dom_err_codes {
    DOM_OK = 0,
    DOM_ERR_UNKNOWN = 1,
    DOM_ERR_INVALID_ARG = 2,
    DOM_ERR_OUT_OF_MEMORY = 3,
    DOM_ERR_OVERFLOW = 4,
    DOM_ERR_UNDERFLOW = 5,
    DOM_ERR_BOUNDS = 6,
    DOM_ERR_NOT_FOUND = 7,
    DOM_ERR_NOT_IMPLEMENTED = 8,
    DOM_ERR_IO = 9
};

const char *dom_err_str(dom_err_t code);

#endif /* DOM_CORE_ERR_H */
