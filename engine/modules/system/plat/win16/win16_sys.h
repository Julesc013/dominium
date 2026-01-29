/*
FILE: source/domino/system/plat/win16/win16_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/win16
RESPONSIBILITY: Declares Win16 backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_WIN16_SYS_H
#define DSYS_WIN16_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_win16_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_WIN16_SYS_H */
