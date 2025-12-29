/*
FILE: include/dominium/core_audit.h
MODULE: Dominium
PURPOSE: Placeholder shared audit helpers (R-1 scaffolding; implementation lives in kernel modules).
*/
#ifndef DOMINIUM_CORE_AUDIT_H
#define DOMINIUM_CORE_AUDIT_H

typedef struct dom_core_audit_sink {
    const char *path;
} dom_core_audit_sink;

#endif /* DOMINIUM_CORE_AUDIT_H */
