#include "dom_core_rng.h"

/* Helper to build a 64-bit constant without C99 long long literals. */
#define DOM_U64_CONST(hi, lo) ((((dom_u64)(hi)) << 32) | (dom_u64)(lo))

void dom_rng_seed(dom_rng *rng, dom_u64 seed)
{
    if (!rng) return;
    rng->s0 = seed;
    rng->s1 = seed ^ DOM_U64_CONST(0x9E3779B9u, 0x7F4A7C15u);
}

dom_u32 dom_rng_u32(dom_rng *rng)
{
    if (!rng) return 0;
    rng->s0 += DOM_U64_CONST(0x9E3779B9u, 0x7F4A7C15u);
    return (dom_u32)(rng->s0 >> 32);
}

dom_u64 dom_rng_u64(dom_rng *rng)
{
    if (!rng) return 0;
    rng->s0 += DOM_U64_CONST(0x9E3779B9u, 0x7F4A7C15u);
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
