/*
FILE: source/domino/core/rng_model.c
MODULE: Domino
RESPONSIBILITY: Implements named RNG stream derivation and validation.
*/
#include "domino/core/rng_model.h"

#include <string.h>

static char d_rng_ascii_lower(char c)
{
    if (c >= 'A' && c <= 'Z') {
        return (char)(c + ('a' - 'A'));
    }
    return c;
}

u32 d_rng_fold_u64(u64 value)
{
    return (u32)(value ^ (value >> 32));
}

u32 d_rng_hash_str32(const char* text)
{
    u32 h = 2166136261u;
    const unsigned char* p = (const unsigned char*)text;
    if (!text) {
        return 0u;
    }
    while (*p) {
        h ^= (u32)(*p++);
        h *= 16777619u;
    }
    return h;
}

static int d_rng_is_stream_char(char c)
{
    if (c >= 'a' && c <= 'z') return 1;
    if (c >= 'A' && c <= 'Z') return 1;
    if (c >= '0' && c <= '9') return 1;
    if (c == '-' || c == '_') return 1;
    return 0;
}

int d_rng_stream_name_valid(const char* name)
{
    const char* prefix = "noise.stream.";
    const size_t prefix_len = strlen(prefix);
    size_t name_len;
    size_t i;
    int segment_count = 0;
    int segment_len = 0;
    const char* p;

    if (!name) {
        return 0;
    }
    name_len = strlen(name);
    if (name_len <= prefix_len) {
        return 0;
    }
    for (i = 0u; i < prefix_len; ++i) {
        char a = d_rng_ascii_lower(name[i]);
        char b = prefix[i];
        if (a != b) {
            return 0;
        }
    }
    p = name + prefix_len;
    if (*p == '\0') {
        return 0;
    }
    for (; *p; ++p) {
        char c = *p;
        if (c == '.') {
            if (segment_len == 0) {
                return 0;
            }
            segment_count += 1;
            segment_len = 0;
            continue;
        }
        if (!d_rng_is_stream_char(c)) {
            return 0;
        }
        segment_len += 1;
    }
    if (segment_len == 0) {
        return 0;
    }
    return segment_count >= 2 ? 1 : 0;
}

u32 d_rng_seed_from_context(u64 world_seed,
                            u64 domain_id,
                            u64 process_id,
                            u64 tick_index,
                            const char* stream_name,
                            u32 mix_flags)
{
    u32 seed = d_rng_fold_u64(world_seed);
    if (mix_flags & D_RNG_MIX_DOMAIN) {
        seed ^= d_rng_fold_u64(domain_id);
    }
    if (mix_flags & D_RNG_MIX_PROCESS) {
        seed ^= d_rng_fold_u64(process_id);
    }
    if (mix_flags & D_RNG_MIX_TICK) {
        seed ^= d_rng_fold_u64(tick_index);
    }
    if (mix_flags & D_RNG_MIX_STREAM) {
        D_DET_GUARD_RNG_STREAM_NAME(stream_name);
        seed ^= d_rng_hash_str32(stream_name);
    }
    return seed;
}

void d_rng_state_from_context(d_rng_state* rng,
                              u64 world_seed,
                              u64 domain_id,
                              u64 process_id,
                              u64 tick_index,
                              const char* stream_name,
                              u32 mix_flags)
{
    u32 seed;
    if (!rng) {
        return;
    }
    seed = d_rng_seed_from_context(world_seed, domain_id, process_id, tick_index, stream_name, mix_flags);
    d_rng_seed(rng, seed);
}

void d_rng_state_from_seed(d_rng_state* rng, u32 seed, const char* stream_name)
{
    if (!rng) {
        return;
    }
    D_DET_GUARD_RNG_STREAM_NAME(stream_name);
    d_rng_seed(rng, seed);
}
