/*
FILE: source/dominium/setup/core/src/util/dsu_util_digest.c
MODULE: Dominium Setup
PURPOSE: Deterministic non-cryptographic digests (FNV-1a 32/64).
*/
#include "dsu_util_internal.h"

dsu_u32 dsu_digest32_init(void) {
    return 2166136261u;
}

dsu_u32 dsu_digest32_update(dsu_u32 state, const void *bytes, dsu_u32 len) {
    const dsu_u8 *p;
    dsu_u32 h;
    dsu_u32 i;
    if (!bytes && len != 0u) {
        return state;
    }
    p = (const dsu_u8 *)bytes;
    h = state;
    for (i = 0u; i < len; ++i) {
        h ^= (dsu_u32)p[i];
        h *= 16777619u;
    }
    return h;
}

dsu_u32 dsu_digest32_bytes(const void *bytes, dsu_u32 len) {
    return dsu_digest32_update(dsu_digest32_init(), bytes, len);
}

dsu_u32 dsu_digest32_str(const char *s) {
    dsu_u32 n;
    if (!s) {
        return 0u;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return 0u;
    }
    return dsu_digest32_bytes(s, n);
}

dsu_u64 dsu_digest64_init(void) {
    /* 0xcbf29ce484222325 */
    return ((dsu_u64)0xCBF29CE4u << 32) | (dsu_u64)0x84222325u;
}

dsu_u64 dsu_digest64_update(dsu_u64 state, const void *bytes, dsu_u32 len) {
    const dsu_u8 *p;
    dsu_u64 h;
    dsu_u32 i;
    if (!bytes && len != 0u) {
        return state;
    }
    p = (const dsu_u8 *)bytes;
    h = state;
    for (i = 0u; i < len; ++i) {
        h ^= (dsu_u64)p[i];
        /* 0x00000100000001B3 */
        h *= (((dsu_u64)0x00000100u << 32) | (dsu_u64)0x000001B3u);
    }
    return h;
}

dsu_u64 dsu_digest64_bytes(const void *bytes, dsu_u32 len) {
    return dsu_digest64_update(dsu_digest64_init(), bytes, len);
}

dsu_u64 dsu_digest64_str(const char *s) {
    dsu_u32 n;
    if (!s) {
        return (dsu_u64)0u;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return (dsu_u64)0u;
    }
    return dsu_digest64_bytes(s, n);
}
