#include "dom_core_rng.h"

void dom_rng_seed(dom_rng *rng, dom_u64 seed)
{
    if (!rng) return;
    rng->s0 = seed;
    rng->s1 = seed ^ 0x9E3779B97F4A7C15ULL;
}

dom_u32 dom_rng_u32(dom_rng *rng)
{
    if (!rng) return 0;
    rng->s0 += 0x9E3779B97F4A7C15ULL;
    return (dom_u32)(rng->s0 >> 32);
}

dom_u64 dom_rng_u64(dom_rng *rng)
{
    if (!rng) return 0;
    rng->s0 += 0x9E3779B97F4A7C15ULL;
    return rng->s0 ^ rng->s1;
}

dom_i32 dom_rng_i32_range(dom_rng *rng, dom_i32 lo, dom_i32 hi)
{
    if (!rng || lo > hi) return lo;
    {
        dom_u32 span = (dom_u32)(hi - lo + 1);
        return lo + (dom_i32)(dom_rng_u32(rng) % span);
    }
}
