/*
FILE: include/dominium/core_audit.h
MODULE: Dominium
PURPOSE: Shared audit helpers (err_t detail encoding/decoding; deterministic TLV layout).
*/
#ifndef DOMINIUM_CORE_AUDIT_H
#define DOMINIUM_CORE_AUDIT_H

extern "C" {
#include "domino/core/types.h"
}

#include "dom_contracts/core_err.h"
#include "dom_contracts/core_tlv.h"

typedef struct dom_core_audit_sink {
    const char *path;
} dom_core_audit_sink;

#endif /* DOMINIUM_CORE_AUDIT_H */
