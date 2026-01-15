/*
FILE: source/domino/dactor.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dactor
RESPONSIBILITY: Implements `dactor`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dactor.h"
#include "domino/dzone.h"
#include "domino/dbody.h"

#include <string.h>

#define DACTOR_MAX_SPECIES 64
#define DACTOR_MAX_ACTORS  1024

static Species g_species[DACTOR_MAX_SPECIES];
static SpeciesId g_species_count = 0;

static Actor   g_actors[DACTOR_MAX_ACTORS];
static bool    g_actor_used[DACTOR_MAX_ACTORS];
static ActorId g_actor_count = 0;

static SubstanceId g_o2_substance = 1;
static SubstanceId g_co2_substance = 2;
static SubstanceId g_h2o_substance = 3;

static Q48_16 dactor_mul_q48_q16(Q48_16 a, Q16_16 b)
{
    return (Q48_16)(((I64)a * (I64)b) >> 16);
}

SpeciesId dactor_species_register(const Species *def)
{
    Species copy;
    if (!def || !def->name) return 0;
    if (g_species_count >= (SpeciesId)DACTOR_MAX_SPECIES) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (SpeciesId)(g_species_count + 1);
    }
    g_species[g_species_count] = copy;
    g_species_count++;
    return copy.id;
}

const Species *dactor_species_get(SpeciesId id)
{
    if (id == 0 || id > g_species_count) return 0;
    return &g_species[id - 1];
}

ActorId dactor_create(SpeciesId species, EnvironmentKind env)
{
    U32 i;
    Actor *a = 0;
    for (i = 0; i < DACTOR_MAX_ACTORS; ++i) {
        if (!g_actor_used[i]) {
            g_actor_used[i] = true;
            a = &g_actors[i];
            g_actor_count = (ActorId)((i + 1 > g_actor_count) ? (i + 1) : g_actor_count);
            break;
        }
    }
    if (!a) return 0;
    memset(a, 0, sizeof(*a));
    a->id = (ActorId)(i + 1);
    a->species = species;
    a->env = env;
    a->health_0_1 = (Q16_16)(1 << 16);
    a->stamina_0_1 = (Q16_16)(1 << 16);
    return a->id;
}

Actor *dactor_get(ActorId id)
{
    if (id == 0 || id > g_actor_count) return 0;
    if (!g_actor_used[id - 1]) return 0;
    return &g_actors[id - 1];
}

void dactor_destroy(ActorId id)
{
    Actor *a = dactor_get(id);
    if (!a) return;
    g_actor_used[id - 1] = false;
}

void dactor_set_substance_ids(SubstanceId o2, SubstanceId co2, SubstanceId h2o)
{
    if (o2) g_o2_substance = o2;
    if (co2) g_co2_substance = co2;
    if (h2o) g_h2o_substance = h2o;
}

static Q16_16 dactor_fraction_q4_to_q16(FractionQ4_12 f)
{
    return (Q16_16)((Q16_16)f << 4);
}

static Q16_16 dactor_clamp_q16(Q16_16 v, Q16_16 lo, Q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static void dactor_update_health(Actor *a, bool satisfied, Q16_16 temp_penalty, Q16_16 pressure_penalty)
{
    Q16_16 delta = 0;
    if (!a) return;
    if (satisfied && temp_penalty == 0 && pressure_penalty == 0) {
        if (a->stamina_0_1 < (Q16_16)(1 << 16)) {
            a->stamina_0_1 += (Q16_16)(1 << 10);
            if (a->stamina_0_1 > (Q16_16)(1 << 16)) a->stamina_0_1 = (Q16_16)(1 << 16);
        }
        return;
    }
    delta = (Q16_16)((1 << 10) + temp_penalty + pressure_penalty);
    if (a->health_0_1 > delta) {
        a->health_0_1 -= delta;
    } else {
        a->health_0_1 = 0;
    }
}

static const Zone *dactor_zone(const Actor *a)
{
    if (!a || a->zone == 0) return 0;
    return dzone_get(a->zone);
}

static void dactor_tick_actor(Actor *a, SimTick t)
{
    const Species *sp;
    Q16_16 dt = g_domino_dt_s;
    Q48_16 o2_req;
    Q48_16 co2_out;
    Q48_16 h2o_req;
    Q48_16 heat;
    bool satisfied = true;
    Q16_16 temp_penalty = 0;
    Q16_16 pressure_penalty = 0;
    PressurePa env_pressure = (PressurePa)(101 << 16);
    TempK env_temp = (TempK)(288 << 16);
    Q16_16 env_o2_frac = (Q16_16)13763; /* approx 0.21 */
    Q16_16 env_co2_frac = 0;
    const Zone *z = 0;
    (void)t;

    sp = dactor_species_get(a->species);
    if (!sp) return;
    o2_req = dactor_mul_q48_q16(sp->o2_consumption_kg_s, dt);
    co2_out = dactor_mul_q48_q16(sp->co2_production_kg_s, dt);
    h2o_req = dactor_mul_q48_q16(sp->h2o_consumption_kg_s, dt);
    heat = dactor_mul_q48_q16(sp->heat_output_W, dt);

    z = dactor_zone(a);
    if (z) {
        env_pressure = z->pressure_Pa;
        env_temp = z->temp_K;
        /* find fractions */
        {
            U8 i;
            for (i = 0; i < z->atm.count; ++i) {
                if (z->atm.substance[i] == g_o2_substance) {
                    env_o2_frac = dactor_fraction_q4_to_q16(z->atm.frac[i]);
                } else if (z->atm.substance[i] == g_co2_substance) {
                    env_co2_frac = dactor_fraction_q4_to_q16(z->atm.frac[i]);
                }
            }
        }
    }

    if (env_pressure < sp->min_pressure_Pa || env_pressure > sp->max_pressure_Pa) {
        pressure_penalty = (Q16_16)(1 << 12);
        satisfied = false;
    }
    if (env_temp < sp->min_temp_K || env_temp > sp->max_temp_K) {
        temp_penalty = (Q16_16)(1 << 12);
        satisfied = false;
    }
    if (env_o2_frac < sp->min_o2_fraction || env_co2_frac > sp->max_co2_fraction) {
        satisfied = false;
    }

    if (z && satisfied) {
        /* consume O2, produce CO2, add heat */
        if (!dzone_add_gas(z->id, g_o2_substance, -o2_req, 0)) {
            satisfied = false;
        } else {
            dzone_add_gas(z->id, g_co2_substance, co2_out, 0);
            dzone_add_heat(z->id, heat);
        }
    }

    dactor_update_health(a, satisfied, temp_penalty, pressure_penalty);
    (void)h2o_req;
    if (a->body_temp_K == 0) {
        a->body_temp_K = env_temp;
    } else {
        a->body_temp_K = (TempK)((a->body_temp_K + env_temp) / 2);
    }
}

void dactor_tick_all(SimTick t)
{
    U32 i;
    for (i = 0; i < g_actor_count; ++i) {
        if (g_actor_used[i]) {
            dactor_tick_actor(&g_actors[i], t);
        }
    }
}
