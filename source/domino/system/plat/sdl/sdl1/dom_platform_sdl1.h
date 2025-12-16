/*
FILE: source/domino/system/plat/sdl/sdl1/dom_platform_sdl1.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/sdl/sdl1/dom_platform_sdl1
RESPONSIBILITY: Defines internal contract for `dom_platform_sdl1`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_PLATFORM_SDL1_H
#define DOM_PLATFORM_SDL1_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

int  dom_platform_sdl1_init(void);
void dom_platform_sdl1_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_SDL1_H */
