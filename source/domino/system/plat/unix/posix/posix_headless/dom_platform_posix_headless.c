/*
FILE: source/domino/system/plat/unix/posix/posix_headless/dom_platform_posix_headless.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/unix/posix/posix_headless/dom_platform_posix_headless
RESPONSIBILITY: Implements `dom_platform_posix_headless`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_platform_posix_headless.h"

int dom_platform_posix_headless_init(void)
{
    /* TODO: implement CLI timers/filesystem/net hooks for POSIX headless. */
    return 0;
}

void dom_platform_posix_headless_shutdown(void)
{
    /* TODO: release any allocated resources when implemented. */
}
