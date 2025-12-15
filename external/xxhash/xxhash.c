#include "xxhash.h"

#include <string.h>

#define DOM_XXH_PRIME64_1 11400714785074694791ULL
#define DOM_XXH_PRIME64_2 14029467366897019727ULL
#define DOM_XXH_PRIME64_3  1609587929392839161ULL
#define DOM_XXH_PRIME64_4  9650029242287828579ULL
#define DOM_XXH_PRIME64_5  2870177450012600261ULL

static u64 dom_xxh_rotl64(u64 x, u32 r)
{
    return (x << r) | (x >> (64u - r));
}

static u64 dom_xxh_read64_le(const unsigned char* p)
{
    return ((u64)p[0]) |
           ((u64)p[1] << 8) |
           ((u64)p[2] << 16) |
           ((u64)p[3] << 24) |
           ((u64)p[4] << 32) |
           ((u64)p[5] << 40) |
           ((u64)p[6] << 48) |
           ((u64)p[7] << 56);
}

static u32 dom_xxh_read32_le(const unsigned char* p)
{
    return ((u32)p[0]) |
           ((u32)p[1] << 8) |
           ((u32)p[2] << 16) |
           ((u32)p[3] << 24);
}

static u64 dom_xxh_round(u64 acc, u64 input)
{
    acc += input * (u64)DOM_XXH_PRIME64_2;
    acc = dom_xxh_rotl64(acc, 31u);
    acc *= (u64)DOM_XXH_PRIME64_1;
    return acc;
}

static u64 dom_xxh_merge_round(u64 acc, u64 val)
{
    val = dom_xxh_round(0u, val);
    acc ^= val;
    acc = acc * (u64)DOM_XXH_PRIME64_1 + (u64)DOM_XXH_PRIME64_4;
    return acc;
}

static u64 dom_xxh_avalanche(u64 h)
{
    h ^= h >> 33;
    h *= (u64)DOM_XXH_PRIME64_2;
    h ^= h >> 29;
    h *= (u64)DOM_XXH_PRIME64_3;
    h ^= h >> 32;
    return h;
}

u64 dom_xxhash64(const void* data, size_t len, u64 seed)
{
    const unsigned char* p = (const unsigned char*)data;
    const unsigned char* const b_end = p + len;
    u64 h64;

    if (!p) {
        return 0u;
    }

    if (len >= 32u) {
        const unsigned char* const limit = b_end - 32u;
        u64 v1 = seed + (u64)DOM_XXH_PRIME64_1 + (u64)DOM_XXH_PRIME64_2;
        u64 v2 = seed + (u64)DOM_XXH_PRIME64_2;
        u64 v3 = seed + 0u;
        u64 v4 = seed - (u64)DOM_XXH_PRIME64_1;

        do {
            v1 = dom_xxh_round(v1, dom_xxh_read64_le(p)); p += 8;
            v2 = dom_xxh_round(v2, dom_xxh_read64_le(p)); p += 8;
            v3 = dom_xxh_round(v3, dom_xxh_read64_le(p)); p += 8;
            v4 = dom_xxh_round(v4, dom_xxh_read64_le(p)); p += 8;
        } while (p <= limit);

        h64 = dom_xxh_rotl64(v1, 1u) +
              dom_xxh_rotl64(v2, 7u) +
              dom_xxh_rotl64(v3, 12u) +
              dom_xxh_rotl64(v4, 18u);

        h64 = dom_xxh_merge_round(h64, v1);
        h64 = dom_xxh_merge_round(h64, v2);
        h64 = dom_xxh_merge_round(h64, v3);
        h64 = dom_xxh_merge_round(h64, v4);
    } else {
        h64 = seed + (u64)DOM_XXH_PRIME64_5;
    }

    h64 += (u64)len;

    while (p + 8u <= b_end) {
        u64 k1 = dom_xxh_read64_le(p);
        k1 *= (u64)DOM_XXH_PRIME64_2;
        k1 = dom_xxh_rotl64(k1, 31u);
        k1 *= (u64)DOM_XXH_PRIME64_1;
        h64 ^= k1;
        h64 = dom_xxh_rotl64(h64, 27u) * (u64)DOM_XXH_PRIME64_1 + (u64)DOM_XXH_PRIME64_4;
        p += 8u;
    }

    if (p + 4u <= b_end) {
        h64 ^= (u64)dom_xxh_read32_le(p) * (u64)DOM_XXH_PRIME64_1;
        h64 = dom_xxh_rotl64(h64, 23u) * (u64)DOM_XXH_PRIME64_2 + (u64)DOM_XXH_PRIME64_3;
        p += 4u;
    }

    while (p < b_end) {
        h64 ^= ((u64)(*p)) * (u64)DOM_XXH_PRIME64_5;
        h64 = dom_xxh_rotl64(h64, 11u) * (u64)DOM_XXH_PRIME64_1;
        p += 1u;
    }

    return dom_xxh_avalanche(h64);
}

