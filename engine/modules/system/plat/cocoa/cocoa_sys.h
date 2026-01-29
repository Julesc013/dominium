/*
FILE: source/domino/system/plat/cocoa/cocoa_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/cocoa
RESPONSIBILITY: Declares Cocoa backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_COCOA_SYS_H
#define DSYS_COCOA_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_cocoa_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_COCOA_SYS_H */
