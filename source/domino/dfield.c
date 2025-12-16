/*
FILE: source/domino/dfield.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dfield
RESPONSIBILITY: Implements `dfield`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dfield.h"
#include "domino/dnumeric.h"

#include <string.h>

#define DFIELD_MAX_FIELDS 256

static FieldDesc g_fields[DFIELD_MAX_FIELDS];
static FieldId   g_field_count = 0;
static bool      g_field_bootstrapped = false;

static FieldId g_field_terrain_height;
static FieldId g_field_water_depth;
static FieldId g_field_soil_moisture;
static FieldId g_field_fertility;
static FieldId g_field_air_pressure;
static FieldId g_field_air_temp;
static FieldId g_field_humidity;
static FieldId g_field_wind_u;
static FieldId g_field_wind_v;
static FieldId g_field_pollution;
static FieldId g_field_radiation;
static FieldId g_field_noise_level;
static FieldId g_field_cloud_cover;
static FieldId g_field_biome_id;
static FieldId g_field_climate_mean_temp;
static FieldId g_field_climate_mean_precip;
static FieldId g_field_climate_mean_humidity;

static FieldId dfield_register_internal(const FieldDesc *def)
{
    FieldDesc copy;
    FieldId i;
    if (!def || !def->name) return 0;
    if (g_field_count >= (FieldId)DFIELD_MAX_FIELDS) return 0;

    for (i = 0; i < g_field_count; ++i) {
        if (g_fields[i].name && strcmp(g_fields[i].name, def->name) == 0) {
            return g_fields[i].id;
        }
    }

    copy = *def;
    copy.id = (FieldId)(g_field_count + 1);
    g_fields[g_field_count] = copy;
    g_field_count++;
    return copy.id;
}

static void dfield_bootstrap(void)
{
    FieldDesc def;
    if (g_field_bootstrapped) return;
    g_field_bootstrapped = true;

    memset(&def, 0, sizeof(def));

    def.name = "terrain_height";
    def.unit = UNIT_HEIGHT_M;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_terrain_height = dfield_register_internal(&def);

    def.name = "water_depth";
    def.unit = UNIT_DEPTH_M;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_water_depth = dfield_register_internal(&def);

    def.name = "soil_moisture";
    def.unit = UNIT_FRACTION;
    def.storage = FIELD_STORAGE_Q4_12;
    g_field_soil_moisture = dfield_register_internal(&def);

    def.name = "fertility";
    def.unit = UNIT_FRACTION;
    def.storage = FIELD_STORAGE_Q4_12;
    g_field_fertility = dfield_register_internal(&def);

    def.name = "air_pressure";
    def.unit = UNIT_PRESSURE_PA;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_air_pressure = dfield_register_internal(&def);

    def.name = "air_temp";
    def.unit = UNIT_TEMP_K;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_air_temp = dfield_register_internal(&def);

    def.name = "humidity";
    def.unit = UNIT_FRACTION;
    def.storage = FIELD_STORAGE_Q4_12;
    g_field_humidity = dfield_register_internal(&def);

    def.name = "wind_u";
    def.unit = UNIT_WIND_M_S;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_wind_u = dfield_register_internal(&def);

    def.name = "wind_v";
    def.unit = UNIT_WIND_M_S;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_wind_v = dfield_register_internal(&def);

    def.name = "pollution";
    def.unit = UNIT_POLLUTION;
    def.storage = FIELD_STORAGE_U8;
    g_field_pollution = dfield_register_internal(&def);

    def.name = "radiation";
    def.unit = UNIT_RADIATION_SV_S;
    def.storage = FIELD_STORAGE_U8;
    g_field_radiation = dfield_register_internal(&def);

    def.name = "noise_level";
    def.unit = UNIT_NOISE;
    def.storage = FIELD_STORAGE_U8;
    g_field_noise_level = dfield_register_internal(&def);

    def.name = "cloud_cover";
    def.unit = UNIT_FRACTION;
    def.storage = FIELD_STORAGE_Q4_12;
    g_field_cloud_cover = dfield_register_internal(&def);

    def.name = "biome_id";
    def.unit = UNIT_NONE;
    def.storage = FIELD_STORAGE_U8;
    g_field_biome_id = dfield_register_internal(&def);

    def.name = "climate_mean_temp";
    def.unit = UNIT_TEMP_K;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_climate_mean_temp = dfield_register_internal(&def);

    def.name = "climate_mean_precip";
    def.unit = UNIT_DEPTH_M;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_climate_mean_precip = dfield_register_internal(&def);

    def.name = "climate_mean_humidity";
    def.unit = UNIT_FRACTION;
    def.storage = FIELD_STORAGE_Q16_16;
    g_field_climate_mean_humidity = dfield_register_internal(&def);
}

FieldId dfield_register(const FieldDesc *def)
{
    dfield_bootstrap();
    return dfield_register_internal(def);
}

const FieldDesc *dfield_get(FieldId id)
{
    dfield_bootstrap();
    if (id == 0) return 0;
    if (id > g_field_count) return 0;
    return &g_fields[id - 1];
}

const FieldDesc *dfield_find_by_name(const char *name)
{
    FieldId i;
    dfield_bootstrap();
    if (!name) return 0;
    for (i = 0; i < g_field_count; ++i) {
        if (g_fields[i].name && strcmp(g_fields[i].name, name) == 0) {
            return &g_fields[i];
        }
    }
    return 0;
}

Q4_12 dfield_q16_to_q4(FieldId id, Q16_16 v)
{
    const FieldDesc *desc;
    (void)id;
    desc = dfield_get(id);
    if (desc && desc->storage != FIELD_STORAGE_Q4_12) {
        /* TODO: encode via proper storage codec per field */
    }
    return dnum_q16_to_q4(v);
}

Q16_16 dfield_q4_to_q16(FieldId id, Q4_12 raw)
{
    const FieldDesc *desc;
    (void)id;
    desc = dfield_get(id);
    if (desc && desc->storage != FIELD_STORAGE_Q4_12) {
        /* TODO: decode via proper storage codec per field */
    }
    return dnum_q4_to_q16(raw);
}

U8 dfield_q16_to_u8(FieldId id, Q16_16 v)
{
    const FieldDesc *desc;
    I32 i;
    (void)id;
    desc = dfield_get(id);
    if (desc && desc->storage != FIELD_STORAGE_U8) {
        /* TODO: encode per-field range instead of naïve clamp */
    }
    i = dnum_to_int32(v);
    if (i < 0) i = 0;
    if (i > 255) i = 255;
    return (U8)i;
}

Q16_16 dfield_u8_to_q16(FieldId id, U8 raw)
{
    const FieldDesc *desc;
    (void)id;
    desc = dfield_get(id);
    if (desc && desc->storage != FIELD_STORAGE_U8) {
        /* TODO: decode per-field range instead of 1:1 scaling */
    }
    return dnum_from_int32((I32)raw);
}
