#include "domino/dbiome.h"
#include "domino/dclimate.h"
#include "domino/dhydro.h"

#include <string.h>

#define DBIOME_MAX_TYPES 64

static BiomeType g_biomes[DBIOME_MAX_TYPES];
static U32       g_biome_count = 0;
static FieldId   g_field_biome_id;

static bool dbiome_range_match(Q16_16 v, Q16_16 min_v, Q16_16 max_v)
{
    if (min_v == 0 && max_v == 0) return true;
    if (v < min_v) return false;
    if (max_v != 0 && v > max_v) return false;
    return true;
}

static bool dbiome_temp_match(TempK t, TempK min_t, TempK max_t)
{
    if (min_t == 0 && max_t == 0) return true;
    if (t < min_t) return false;
    if (max_t != 0 && t > max_t) return false;
    return true;
}

static void dbiome_register_defaults(void)
{
    BiomeType def;
    if (g_biome_count > 0) return;
    memset(&def, 0, sizeof(def));

    def.id = 1;
    def.name = "temperate_forest";
    def.min_temp = (TempK)(270 << 16);
    def.max_temp = (TempK)(305 << 16);
    def.min_precip = (Q16_16)(1 << 16);
    def.max_precip = (Q16_16)(4 << 16);
    def.min_humidity = (Q16_16)(1 << 15);
    def.max_humidity = (Q16_16)(1 << 16);
    dbiome_register_type(&def);

    def.id = 2;
    def.name = "desert";
    def.min_temp = (TempK)(285 << 16);
    def.max_temp = (TempK)(350 << 16);
    def.min_precip = 0;
    def.max_precip = (Q16_16)(1 << 16);
    def.min_humidity = 0;
    def.max_humidity = (Q16_16)(1 << 15);
    dbiome_register_type(&def);

    def.id = 3;
    def.name = "tundra";
    def.min_temp = 0;
    def.max_temp = (TempK)(275 << 16);
    def.min_precip = 0;
    def.max_precip = (Q16_16)(2 << 16);
    def.min_humidity = 0;
    def.max_humidity = (Q16_16)(1 << 16);
    def.min_height = (Q16_16)(300 << 16);
    def.max_height = 0;
    dbiome_register_type(&def);

    def.id = 4;
    def.name = "wetland";
    def.min_temp = (TempK)(260 << 16);
    def.max_temp = (TempK)(320 << 16);
    def.min_precip = (Q16_16)(2 << 16);
    def.max_precip = 0;
    def.min_humidity = (Q16_16)(1 << 15);
    def.max_humidity = 0;
    def.min_height = 0;
    def.max_height = (Q16_16)(100 << 16);
    dbiome_register_type(&def);
}

FieldId dbiome_field_biome_id(void)
{
    if (g_field_biome_id != 0) return g_field_biome_id;
    {
        FieldDesc def;
        memset(&def, 0, sizeof(def));
        def.name = "biome_id";
        def.unit = UNIT_NONE;
        def.storage = FIELD_STORAGE_U8;
        g_field_biome_id = dfield_register(&def);
    }
    return g_field_biome_id;
}

bool dbiome_register_type(const BiomeType *type)
{
    BiomeType copy;
    U32 i;
    if (!type || !type->name) return false;
    if (g_biome_count >= DBIOME_MAX_TYPES) return false;
    for (i = 0; i < g_biome_count; ++i) {
        if (g_biomes[i].id == type->id || (g_biomes[i].name && strcmp(g_biomes[i].name, type->name) == 0)) {
            g_biomes[i] = *type;
            return true;
        }
    }
    copy = *type;
    if (copy.id == 0) {
        copy.id = (BiomeId)(g_biome_count + 1);
    }
    g_biomes[g_biome_count++] = copy;
    return true;
}

const BiomeType *dbiome_get_type(BiomeId id)
{
    U32 i;
    if (id == 0) return 0;
    for (i = 0; i < g_biome_count; ++i) {
        if (g_biomes[i].id == id) {
            return &g_biomes[i];
        }
    }
    return 0;
}

BiomeId dbiome_classify(BodyId body, TempK temp, Q16_16 precip, Q16_16 humidity, Q16_16 height_m)
{
    U32 i;
    (void)body;
    if (g_biome_count == 0) {
        dbiome_register_defaults();
    }
    for (i = 0; i < g_biome_count; ++i) {
        const BiomeType *b = &g_biomes[i];
        if (!dbiome_temp_match(temp, b->min_temp, b->max_temp)) continue;
        if (!dbiome_range_match(precip, b->min_precip, b->max_precip)) continue;
        if (!dbiome_range_match(humidity, b->min_humidity, b->max_humidity)) continue;
        if (!dbiome_range_match(height_m, b->min_height, b->max_height)) continue;
        return b->id;
    }
    return 0;
}

BiomeId dbiome_get_at_tile(BodyId body, const WPosTile *tile)
{
    TempK temp = 0;
    Q16_16 precip = 0;
    Q16_16 humidity = 0;
    Q16_16 height_m = 0;
    Q16_16 water_depth = 0;
    Q16_16 extra_h = 0;
    if (!tile) return 0;
    height_m = dnum_from_int32((I32)tile->z);
    dclimate_sample_at_tile(body, tile, &temp, &precip, &humidity);
    if (dhydro_get_water_depth(body, tile, &water_depth)) {
        precip += water_depth >> 4;
        extra_h = water_depth >> 5;
        if (extra_h > (Q16_16)((1 << 16) - humidity)) {
            extra_h = (Q16_16)((1 << 16) - humidity);
        }
        humidity += extra_h;
    }
    return dbiome_classify(body, temp, precip, humidity, height_m);
}
