/*
FILE: source/domino/system/plat/wayland/wayland_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/wayland
RESPONSIBILITY: Declares Wayland backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_WAYLAND_SYS_H
#define DSYS_WAYLAND_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_wayland_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_WAYLAND_SYS_H */
