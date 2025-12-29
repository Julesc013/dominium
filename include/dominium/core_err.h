/*
FILE: include/dominium/core_err.h
MODULE: Dominium
PURPOSE: Placeholder error domain for shared kernel modules (R-1 scaffolding).
*/
#ifndef DOMINIUM_CORE_ERR_H
#define DOMINIUM_CORE_ERR_H

typedef enum dom_core_err {
    DOM_CORE_OK = 0,
    DOM_CORE_ERR = 1,
    DOM_CORE_ERR_INVALID_ARGS = 2,
    DOM_CORE_ERR_UNSUPPORTED = 3
} dom_core_err;

#endif /* DOMINIUM_CORE_ERR_H */
