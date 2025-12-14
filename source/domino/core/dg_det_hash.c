#include "core/dg_det_hash.h"

u64 dg_det_hash_u64(u64 v) {
    /* SplitMix64 finalizer-style avalanche. */
    v ^= v >> 30;
    v *= 0xbf58476d1ce4e5b9ULL;
    v ^= v >> 27;
    v *= 0x94d049bb133111ebULL;
    v ^= v >> 31;
    return v;
}

