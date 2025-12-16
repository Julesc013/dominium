/*
FILE: source/domino/dzone.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dzone
RESPONSIBILITY: Implements `dzone`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dzone.h"
#include "domino/dbody.h"

#include <string.h>

#define DZONE_MAX_ZONES     1024
#define DZONE_MAX_LINKS     2048

static Zone     g_zones[DZONE_MAX_ZONES];
static ZoneLink g_links[DZONE_MAX_LINKS];
static ZoneId   g_zone_count = 0;
static ZoneLinkId g_link_count = 0;

static Q16_16 dzone_mul_q16(Q16_16 a, Q16_16 b)
{
    return (Q16_16)(((I64)a * (I64)b) >> 16);
}

static Q16_16 dzone_clamp_q16(Q16_16 v, Q16_16 lo, Q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

ZoneId dzone_register(const Zone *def)
{
    ZoneId id;
    Zone *z;
    if (!def) return 0;
    if (g_zone_count >= (ZoneId)DZONE_MAX_ZONES) return 0;
    id = ++g_zone_count;
    z = &g_zones[id - 1];
    *z = *def;
    z->id = id;
    return id;
}

Zone *dzone_get(ZoneId id)
{
    if (id == 0 || id > g_zone_count) return 0;
    return &g_zones[id - 1];
}

ZoneLinkId dzone_link_register(const ZoneLink *def)
{
    ZoneLinkId id;
    ZoneLink *l;
    if (!def) return 0;
    if (g_link_count >= (ZoneLinkId)DZONE_MAX_LINKS) return 0;
    id = ++g_link_count;
    l = &g_links[id - 1];
    *l = *def;
    l->id = id;
    return id;
}

ZoneLink *dzone_link_get(ZoneLinkId id)
{
    if (id == 0 || id > g_link_count) return 0;
    return &g_links[id - 1];
}

U32 dzone_get_by_aggregate(AggregateId agg, ZoneId *out_ids, U32 max_out)
{
    U32 count = 0;
    ZoneId i;
    if (!out_ids || max_out == 0) return 0;
    for (i = 0; i < g_zone_count && count < max_out; ++i) {
        if (g_zones[i].agg == agg) {
            out_ids[count++] = g_zones[i].id;
        }
    }
    return count;
}

static TempK dzone_body_base_temp(BodyId body)
{
    const Body *b = dbody_get(body);
    if (b) return b->base_temp_K;
    return (TempK)(288 << 16);
}

static Q16_16 dzone_mass_to_pressure(Q48_16 mass, Q16_16 volume)
{
    I64 v = (I64)(volume >> 16);
    if (volume == 0 || v == 0) return 0;
    return (Q16_16)(((I64)mass) / v);
}

static TempK dzone_mix_temp(TempK existing_temp, Q48_16 existing_mass, TempK incoming_temp, Q48_16 incoming_mass)
{
    if (incoming_mass <= 0) return existing_temp;
    if (existing_mass <= 0) return incoming_temp;
    {
        I64 num = ((I64)existing_temp * (I64)existing_mass) + ((I64)incoming_temp * (I64)incoming_mass);
        I64 den = (I64)existing_mass + (I64)incoming_mass;
        if (den == 0) return existing_temp;
        return (TempK)(num / den);
    }
}

static void dzone_mix_between(Zone *from, Zone *to, Q16_16 fraction)
{
    Q48_16 mass_from = 0;
    Q48_16 mass_move = 0;
    TempK new_temp_to;
    Q48_16 to_mass_before;
    if (!from || !to) return;
    mass_from = from->atm.total_mass_kg;
    mass_move = (Q48_16)(((I64)mass_from * (I64)fraction) >> 16);
    if (mass_move == 0 || mass_from == 0) return;
    to_mass_before = to->atm.total_mass_kg;
    dmix_transfer_fraction(&from->atm, &to->atm, fraction);
    new_temp_to = dzone_mix_temp(to->temp_K, to_mass_before, from->temp_K, mass_move);
    to->temp_K = new_temp_to;
}

void dzone_tick(SimTick t)
{
    U32 i;
    Q16_16 dt = g_domino_dt_s;
    (void)t;

    /* Gas exchange through links */
    for (i = 0; i < g_link_count; ++i) {
        ZoneLink *l = &g_links[i];
        Zone *za = dzone_get(l->a);
        Zone *zb = dzone_get(l->b);
        Q16_16 dp;
        Q16_16 mag;
        Q16_16 fraction;
        if (!za || !zb) continue;
        dp = (Q16_16)(za->pressure_Pa - zb->pressure_Pa);
        if (dp == 0) continue;
        mag = dzone_mul_q16(l->flow_coeff, l->area_m2);
        mag = dzone_mul_q16(mag, dt);
        fraction = dzone_clamp_q16(mag, 0, (Q16_16)(1 << 16));
        if (dp > 0) {
            dzone_mix_between(za, zb, fraction);
        } else {
            dzone_mix_between(zb, za, fraction);
        }
    }

    /* Leak/thermal to environment and recompute pressures */
    for (i = 0; i < g_zone_count; ++i) {
        Zone *z = &g_zones[i];
        Q16_16 leak_frac = dzone_mul_q16(z->leak_factor_0_1, dt);
        Q16_16 thermal_frac = dzone_mul_q16(z->thermal_leak_0_1, dt);
        TempK env_temp = dzone_body_base_temp(z->body);
        if (leak_frac > 0) {
            Q16_16 leak_clamped = dzone_clamp_q16(leak_frac, 0, (Q16_16)(1 << 16));
            z->atm.total_mass_kg = (Q48_16)(((I64)z->atm.total_mass_kg * (I64)((1 << 16) - leak_clamped)) >> 16);
            dmix_normalise(&z->atm);
        }
        if (thermal_frac > 0) {
            TempK delta = (TempK)(((I64)(env_temp - z->temp_K) * (I64)thermal_frac) >> 16);
            z->temp_K = (TempK)(z->temp_K + delta);
        }
        z->pressure_Pa = dzone_mass_to_pressure(z->atm.total_mass_kg, z->volume_m3);
        if (z->pressure_Pa < 0) z->pressure_Pa = 0;
    }
}

bool dzone_add_gas(ZoneId id, SubstanceId s, MassKg mass_delta_kg, EnergyJ energy_delta_J)
{
    Zone *z = dzone_get(id);
    Q48_16 mass;
    if (!z) return false;
    if (!dmix_add_mass(&z->atm, s, mass_delta_kg)) {
        return false;
    }
    mass = z->atm.total_mass_kg;
    if (energy_delta_J != 0 && mass != 0) {
        TempK delta_T = (TempK)(energy_delta_J / mass);
        z->temp_K = (TempK)(z->temp_K + delta_T);
    }
    dmix_normalise(&z->atm);
    return true;
}

bool dzone_add_heat(ZoneId id, EnergyJ energy_delta_J)
{
    Zone *z = dzone_get(id);
    Q48_16 mass;
    if (!z) return false;
    mass = z->atm.total_mass_kg;
    if (mass == 0) return true;
    z->temp_K = (TempK)(z->temp_K + (TempK)(energy_delta_J / mass));
    return true;
}
