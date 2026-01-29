/*
FILE: source/domino/system/plat/dos16/dos16_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/dos16
RESPONSIBILITY: Declares DOS16 backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_DOS16_SYS_H
#define DSYS_DOS16_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_dos16_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_DOS16_SYS_H */
