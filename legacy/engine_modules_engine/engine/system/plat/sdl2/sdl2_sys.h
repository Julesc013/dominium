/*
FILE: source/domino/system/plat/sdl2/sdl2_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/sdl2/sdl2_sys
RESPONSIBILITY: Defines internal contract for `sdl2_sys`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_SDL2_SYS_H
#define DOMINO_SDL2_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"
#include "../dsys_internal.h"

const dsys_backend_vtable* dsys_sdl2_get_vtable(void);

#endif /* DOMINO_SDL2_SYS_H */
