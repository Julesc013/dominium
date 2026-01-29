/*
FILE: source/domino/system/plat/cpm80/cpm80_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/cpm80
RESPONSIBILITY: Declares CP/M-80 backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_CPM80_SYS_H
#define DSYS_CPM80_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_cpm80_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_CPM80_SYS_H */
