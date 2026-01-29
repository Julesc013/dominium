/*
FILE: source/domino/system/plat/posix/posix_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/posix
RESPONSIBILITY: Declares POSIX headless backend entrypoint.
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Backend provides deterministic directory ordering.
VERSIONING / ABI / DATA FORMAT NOTES: Internal header.
EXTENSION POINTS: Replace with richer POSIX backends (X11/Wayland).
*/
#ifndef DSYS_POSIX_SYS_H
#define DSYS_POSIX_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_posix_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_POSIX_SYS_H */
