/*
FILE: source/domino/system/plat/unix/wayland/dom_platform_posix_wayland.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/unix/wayland/dom_platform_posix_wayland
RESPONSIBILITY: Implements `dom_platform_posix_wayland`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_PLATFORM_POSIX_WAYLAND_H
#define DOM_PLATFORM_POSIX_WAYLAND_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

int  dom_platform_posix_wayland_init(void);
void dom_platform_posix_wayland_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_POSIX_WAYLAND_H */
