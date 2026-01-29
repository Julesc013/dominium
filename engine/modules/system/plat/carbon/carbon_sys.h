/*
FILE: source/domino/system/plat/carbon/carbon_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/carbon
RESPONSIBILITY: Declares Carbon backend entrypoint (stub or real).
ALLOWED DEPENDENCIES: `include/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`.
*/
#ifndef DSYS_CARBON_SYS_H
#define DSYS_CARBON_SYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

const dsys_backend_vtable* dsys_carbon_get_vtable(void);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_CARBON_SYS_H */
