/*
FILE: tests/determinism/test_spacetime_conversions.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/determinism
RESPONSIBILITY: Determinism checks for tick-based spacetime conversions.
ALLOWED DEPENDENCIES: Project-local headers; C89 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "domino/core/spacetime.h"

static int fail(const char *msg) {
    printf("FAIL: %s\n", msg);
    return 1;
}

int main(void) {
    u64 out = 0ull;
    if (dom_ticks_to_us(60u, 60u, &out) != DOM_SPACETIME_OK || out != 1000000ull) {
        return fail("ticks_to_us 60@60 mismatch");
    }
    if (dom_ticks_to_us(120u, 60u, &out) != DOM_SPACETIME_OK || out != 2000000ull) {
        return fail("ticks_to_us 120@60 mismatch");
    }
    if (dom_ticks_to_us(1u, 60u, &out) != DOM_SPACETIME_OK || out != 16666ull) {
        return fail("ticks_to_us 1@60 mismatch");
    }
    if (dom_ticks_to_ns(60u, 60u, &out) != DOM_SPACETIME_OK || out != 1000000000ull) {
        return fail("ticks_to_ns 60@60 mismatch");
    }
    printf("spacetime conversion tests passed\n");
    return 0;
}
