/*
FILE: source/domino/dmatter.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dmatter
RESPONSIBILITY: Implements `dmatter`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dmatter.h"

#include <string.h>

#define DMATTER_MAX_SUBSTANCES 256
#define DMATTER_MAX_MATERIALS  512
#define DMATTER_MAX_ITEMS      1024

static Substance    g_substances[DMATTER_MAX_SUBSTANCES];
static SubstanceId  g_substance_count = 0;

static MaterialType g_materials[DMATTER_MAX_MATERIALS];
static MaterialId   g_material_count = 0;

static ItemType     g_items[DMATTER_MAX_ITEMS];
static ItemTypeId   g_item_count = 0;

static Q48_16 dmatter_div_q48(Q48_16 num, Q16_16 den_q16)
{
    if (den_q16 == 0) return 0;
    return (Q48_16)(((I64)num << 16) / (I64)den_q16);
}

static Q16_16 dmatter_frac_from_q48(Q48_16 num, Q48_16 den)
{
    if (den == 0) return 0;
    return (Q16_16)(((I64)num << 16) / (I64)den);
}

static Q48_16 dmatter_mul_q48_q16(Q48_16 a, Q16_16 b)
{
    return (Q48_16)(((I64)a * (I64)b) >> 16);
}

static Q48_16 dmatter_abs_q48(Q48_16 v)
{
    return (v < 0) ? -v : v;
}

SubstanceId dmatter_register_substance(const Substance *def)
{
    Substance copy;
    if (!def || !def->name) return 0;
    if (g_substance_count >= (SubstanceId)DMATTER_MAX_SUBSTANCES) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (SubstanceId)(g_substance_count + 1);
    }
    g_substances[g_substance_count] = copy;
    g_substance_count++;
    return copy.id;
}

MaterialId dmatter_register_material(const MaterialType *def)
{
    MaterialType copy;
    if (!def || !def->name) return 0;
    if (g_material_count >= (MaterialId)DMATTER_MAX_MATERIALS) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (MaterialId)(g_material_count + 1);
    }
    g_materials[g_material_count] = copy;
    g_material_count++;
    return copy.id;
}

ItemTypeId dmatter_register_item_type(const ItemType *def)
{
    ItemType copy;
    if (!def || !def->name) return 0;
    if (g_item_count >= (ItemTypeId)DMATTER_MAX_ITEMS) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (ItemTypeId)(g_item_count + 1);
    }
    g_items[g_item_count] = copy;
    g_item_count++;
    return copy.id;
}

const Substance *dmatter_get_substance(SubstanceId id)
{
    if (id == 0) return 0;
    if (id > g_substance_count) return 0;
    return &g_substances[id - 1];
}

const MaterialType *dmatter_get_material(MaterialId id)
{
    if (id == 0) return 0;
    if (id > g_material_count) return 0;
    return &g_materials[id - 1];
}

const ItemType *dmatter_get_item_type(ItemTypeId id)
{
    if (id == 0) return 0;
    if (id > g_item_count) return 0;
    return &g_items[id - 1];
}

void dmix_clear(Mixture *mix)
{
    if (!mix) return;
    memset(mix, 0, sizeof(*mix));
}

static int dmix_find_component(const Mixture *mix, SubstanceId s)
{
    U8 i;
    if (!mix) return -1;
    for (i = 0; i < mix->count; ++i) {
        if (mix->substance[i] == s) {
            return (int)i;
        }
    }
    return -1;
}

static Q48_16 dmix_component_mass(const Mixture *mix, U8 idx)
{
    Q48_16 total;
    if (!mix) return 0;
    if (idx >= mix->count) return 0;
    total = mix->total_mass_kg;
    return (Q48_16)(((I64)total * (I64)mix->frac[idx]) >> 12);
}

static void dmix_recompute_fractions(Mixture *mix)
{
    Q48_16 masses[DMIX_MAX_COMPONENTS];
    Q48_16 mass_total = 0;
    U8 i;
    if (!mix) return;
    for (i = 0; i < mix->count; ++i) {
        masses[i] = dmix_component_mass(mix, i);
        mass_total += masses[i];
    }
    if (mass_total == 0) {
        for (i = 0; i < mix->count; ++i) {
            mix->frac[i] = 0;
        }
        return;
    }
    for (i = 0; i < mix->count; ++i) {
        mix->frac[i] = (FractionQ4_12)dmatter_frac_from_q48(masses[i], mass_total);
    }
}

static void dmix_recompute_volume(Mixture *mix)
{
    U8 i;
    Q48_16 vol = 0;
    if (!mix) return;
    for (i = 0; i < mix->count; ++i) {
        Q48_16 mass_i = dmix_component_mass(mix, i);
        const Substance *sub = dmatter_get_substance(mix->substance[i]);
        Q16_16 density = sub ? sub->density_kg_m3 : (Q16_16)(1 << 16);
        vol += dmatter_div_q48(mass_i, density);
    }
    mix->total_vol_m3 = vol;
}

bool dmix_normalise(Mixture *mix)
{
    if (!mix) return false;
    if (mix->count == 0 || mix->total_mass_kg == 0) {
        dmix_clear(mix);
        return true;
    }
    dmix_recompute_fractions(mix);
    dmix_recompute_volume(mix);
    return true;
}

bool dmix_add_mass(Mixture *mix, SubstanceId s, MassKg mass_delta_kg)
{
    int idx;
    Q48_16 component_masses[DMIX_MAX_COMPONENTS];
    Q48_16 mass_total = 0;
    U8 i;
    if (!mix || s == 0) return false;
    for (i = 0; i < mix->count; ++i) {
        component_masses[i] = dmix_component_mass(mix, i);
    }
    idx = dmix_find_component(mix, s);
    if (idx < 0) {
        if (mass_delta_kg <= 0) return false;
        if (mix->count >= DMIX_MAX_COMPONENTS) return false;
        idx = mix->count;
        mix->substance[idx] = s;
        mix->frac[idx] = 0;
        mix->count++;
        component_masses[idx] = 0;
    }
    if (mass_delta_kg < 0 && dmatter_abs_q48(mass_delta_kg) > component_masses[idx]) {
        /* underflow */
        return false;
    }
    component_masses[idx] += mass_delta_kg;
    mix->total_mass_kg += mass_delta_kg;
    if (mix->total_mass_kg < 0) mix->total_mass_kg = 0;
    for (i = 0; i < mix->count; ++i) {
        mass_total += component_masses[i];
    }
    if (mass_total == 0) {
        dmix_clear(mix);
        return true;
    }
    /* rebuild fractions */
    for (i = 0; i < mix->count; ++i) {
        mix->frac[i] = (FractionQ4_12)dmatter_frac_from_q48(component_masses[i], mass_total);
    }
    mix->total_mass_kg = mass_total;
    dmix_recompute_volume(mix);
    return true;
}

bool dmix_transfer_fraction(Mixture *from, Mixture *to, Q16_16 fraction_0_1)
{
    U8 i;
    Q48_16 transfer_mass;
    Q48_16 mass_from;
    Q48_16 new_total_from = 0;
    Q48_16 mass_to[DMIX_MAX_COMPONENTS];
    Q48_16 mass_from_arr[DMIX_MAX_COMPONENTS];
    U8 to_count;
    if (!from || !to) return false;
    if (fraction_0_1 <= 0) return true;
    if (fraction_0_1 > (Q16_16)(1 << 16)) fraction_0_1 = (Q16_16)(1 << 16);
    to_count = to->count;
    for (i = 0; i < from->count; ++i) {
        mass_from_arr[i] = dmix_component_mass(from, i);
    }
    for (i = 0; i < to_count; ++i) {
        mass_to[i] = dmix_component_mass(to, i);
    }
    for (i = 0; i < from->count; ++i) {
        SubstanceId s = from->substance[i];
        mass_from = mass_from_arr[i];
        transfer_mass = dmatter_mul_q48_q16(mass_from, fraction_0_1);
        mass_from_arr[i] -= transfer_mass;
        if (transfer_mass == 0) continue;
        /* add to destination */
        {
            int j = dmix_find_component(to, s);
            if (j < 0) {
                if (to_count >= DMIX_MAX_COMPONENTS) return false;
                j = to_count++;
                to->substance[j] = s;
                to->frac[j] = 0;
                mass_to[j] = 0;
            }
            mass_to[j] += transfer_mass;
        }
    }
    /* rebuild from */
    from->total_mass_kg = 0;
    for (i = 0; i < from->count; ++i) {
        new_total_from += mass_from_arr[i];
    }
    from->total_mass_kg = new_total_from;
    if (new_total_from == 0) {
        dmix_clear(from);
    } else {
        for (i = 0; i < from->count; ++i) {
            from->frac[i] = (FractionQ4_12)dmatter_frac_from_q48(mass_from_arr[i], new_total_from);
        }
        dmix_recompute_volume(from);
    }
    /* rebuild to */
    to->count = to_count;
    to->total_mass_kg = 0;
    for (i = 0; i < to_count; ++i) {
        to->total_mass_kg += mass_to[i];
    }
    if (to->total_mass_kg > 0) {
        for (i = 0; i < to_count; ++i) {
            to->frac[i] = (FractionQ4_12)dmatter_frac_from_q48(mass_to[i], to->total_mass_kg);
        }
        dmix_recompute_volume(to);
    } else {
        dmix_clear(to);
    }
    return true;
}
