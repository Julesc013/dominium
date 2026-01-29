/*
FILE: source/domino/system/plat/x11/x11_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/x11
RESPONSIBILITY: Declares X11 backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_X11_SYS_H
#define DSYS_X11_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_x11_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_X11_SYS_H */
