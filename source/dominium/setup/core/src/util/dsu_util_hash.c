/*
FILE: source/dominium/setup/core/src/util/dsu_util_hash.c
MODULE: Dominium Setup
PURPOSE: Deterministic non-cryptographic hashing (FNV-1a 32-bit).
*/
#include "dsu_util_internal.h"

dsu_u32 dsu_hash32_bytes(const void *bytes, dsu_u32 len) {
    return dsu_digest32_bytes(bytes, len);
}

dsu_u32 dsu_hash32_str(const char *s) {
    return dsu_digest32_str(s);
}
