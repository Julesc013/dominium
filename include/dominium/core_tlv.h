/*
FILE: include/dominium/core_tlv.h
MODULE: Dominium
PURPOSE: Placeholder shared TLV helpers (R-1 scaffolding; implementation lives in kernel modules).
*/
#ifndef DOMINIUM_CORE_TLV_H
#define DOMINIUM_CORE_TLV_H

#include <stddef.h>

typedef struct dom_core_tlv_span {
    const unsigned char *data;
    size_t size;
} dom_core_tlv_span;

#endif /* DOMINIUM_CORE_TLV_H */
