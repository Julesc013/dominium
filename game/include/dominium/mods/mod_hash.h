/*
FILE: game/include/dominium/mods/mod_hash.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Deterministic hash helpers for mod manifests and graphs.
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: FNV-1a hash with fixed ordering.
*/
#ifndef DOMINIUM_MODS_MOD_HASH_H
#define DOMINIUM_MODS_MOD_HASH_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

static u64 mod_hash_fnv1a64_init(void) {
    return 1469598103934665603ULL;
}

static u64 mod_hash_fnv1a64_update(u64 hash, const void* data, u32 len) {
    const unsigned char* bytes = (const unsigned char*)data;
    u32 i;
    for (i = 0u; i < len; ++i) {
        hash ^= (u64)bytes[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u64 mod_hash_fnv1a64_update_str(u64 hash, const char* text) {
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_MODS_MOD_HASH_H */
