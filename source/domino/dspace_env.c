/*
FILE: source/domino/dspace_env.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dspace_env
RESPONSIBILITY: Implements `dspace_env`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dspace_env.h"

#define DSPACE_MAX_BELTS 32
#define DSPACE_MAX_MAG   16

static BeltField g_belts[DSPACE_MAX_BELTS];
static int       g_belt_count = 0;

static MagneticField g_mags[DSPACE_MAX_MAG];
static int           g_mag_count = 0;

static Q48_16 dspace_abs_q48(Q48_16 v)
{
    return (v < 0) ? -v : v;
}

static U64 dspace_isqrt_u64(U64 v)
{
    U64 res = 0;
    U64 bit = (U64)1 << 62;
    while (bit > v) bit >>= 2;
    while (bit != 0) {
        if (v >= res + bit) {
            v -= res + bit;
            res = (res >> 1) + bit;
        } else {
            res >>= 1;
        }
        bit >>= 2;
    }
    return res;
}

void dspace_env_register_belt(const BeltField *belt)
{
    if (!belt) return;
    if (g_belt_count >= DSPACE_MAX_BELTS) return;
    g_belts[g_belt_count++] = *belt;
}

void dspace_env_register_magnetic(const MagneticField *mag)
{
    if (!mag) return;
    if (g_mag_count >= DSPACE_MAX_MAG) return;
    g_mags[g_mag_count++] = *mag;
}

Q16_16 dspace_env_radiation_intensity(const SpacePos *pos)
{
    /* TODO: use belts and magnetic fields; stub constant */
    (void)pos;
    return (Q16_16)(1 << 16);
}

Q16_16 dspace_env_belt_density(const SpacePos *pos)
{
    int i;
    if (!pos) return 0;
    for (i = 0; i < g_belt_count; ++i) {
        /* Simple spherical shell check */
        Q48_16 r;
        Q16_16 density = 0;
        U64 x = (U64)(dspace_abs_q48(pos->x) >> 16);
        U64 y = (U64)(dspace_abs_q48(pos->y) >> 16);
        U64 z = (U64)(dspace_abs_q48(pos->z) >> 16);
        U64 sum = x * x + y * y + z * z;
        U64 dist = dspace_isqrt_u64(sum);
        r = (Q48_16)(dist << 16);

        if (r >= g_belts[i].inner_radius_m && r <= g_belts[i].outer_radius_m) {
            density = g_belts[i].density;
            return density;
        }
    }
    return 0;
}
