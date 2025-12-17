/*
FILE: source/dominium/setup/core/src/util/dsu_util_hash.c
MODULE: Dominium Setup
PURPOSE: Deterministic non-cryptographic hashing (FNV-1a 32-bit).
*/
#include "dsu_util_internal.h"

dsu_u32 dsu_hash32_bytes(const void *bytes, dsu_u32 len) {
    const dsu_u8 *p;
    dsu_u32 h;
    dsu_u32 i;
    if (!bytes && len != 0u) {
        return 0u;
    }
    p = (const dsu_u8 *)bytes;
    h = 2166136261u;
    for (i = 0u; i < len; ++i) {
        h ^= (dsu_u32)p[i];
        h *= 16777619u;
    }
    return h;
}

dsu_u32 dsu_hash32_str(const char *s) {
    dsu_u32 n;
    if (!s) {
        return 0u;
    }
    n = dsu__strlen(s);
    return dsu_hash32_bytes(s, n);
}

