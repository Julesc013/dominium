/*
FILE: source/domino/system/plat/cpm86/cpm86_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/cpm86
RESPONSIBILITY: Declares CP/M-86 backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_CPM86_SYS_H
#define DSYS_CPM86_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_cpm86_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_CPM86_SYS_H */
