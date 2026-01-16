/*
FILE: include/dominium/core_util.h
MODULE: Dominium
PURPOSE: Placeholder shared utility helpers (R-1 scaffolding; implementation lives in kernel modules).
*/
#ifndef DOMINIUM_CORE_UTIL_H
#define DOMINIUM_CORE_UTIL_H

typedef struct dom_core_string_view {
    const char *data;
    unsigned long size;
} dom_core_string_view;

#endif /* DOMINIUM_CORE_UTIL_H */
