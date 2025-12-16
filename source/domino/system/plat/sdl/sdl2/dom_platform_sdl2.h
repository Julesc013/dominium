/*
FILE: source/domino/system/plat/sdl/sdl2/dom_platform_sdl2.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/sdl/sdl2/dom_platform_sdl2
RESPONSIBILITY: Defines internal contract for `dom_platform_sdl2`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_PLATFORM_SDL2_H
#define DOM_PLATFORM_SDL2_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

int  dom_platform_sdl2_init(void);
void dom_platform_sdl2_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_SDL2_H */
