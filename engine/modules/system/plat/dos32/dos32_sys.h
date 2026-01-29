/*
FILE: source/domino/system/plat/dos32/dos32_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/dos32
RESPONSIBILITY: Declares DOS32 backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_DOS32_SYS_H
#define DSYS_DOS32_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_dos32_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_DOS32_SYS_H */
