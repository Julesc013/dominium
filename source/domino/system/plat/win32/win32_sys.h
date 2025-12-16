/*
FILE: source/domino/system/plat/win32/win32_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/win32/win32_sys
RESPONSIBILITY: Implements `win32_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_WIN32_SYS_H
#define DOMINO_WIN32_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

const dsys_backend_vtable* dsys_win32_get_vtable(void);
const dsys_backend_vtable* dsys_win32_headless_get_vtable(void);

#endif /* DOMINO_WIN32_SYS_H */
