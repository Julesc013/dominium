/*
FILE: source/domino/system/plat/sdl1/sdl1_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/sdl1
RESPONSIBILITY: Declares SDL1 backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_SDL1_SYS_H
#define DSYS_SDL1_SYS_H

#include "domino/sys.h"

struct dsys_backend_vtable_t;

#ifdef __cplusplus
extern "C" {
#endif

const struct dsys_backend_vtable_t* dsys_sdl1_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_SDL1_SYS_H */
