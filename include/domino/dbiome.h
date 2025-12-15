#ifndef DOMINO_DBIOME_H
#define DOMINO_DBIOME_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dworld.h"
#include "dfield.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint16_t BiomeId;

typedef struct {
    BiomeId     id;
    const char *name;
    /* climate ranges: temp, precip, height, humidity */
    TempK       min_temp;
    TempK       max_temp;
    Q16_16      min_precip;
    Q16_16      max_precip;
    Q16_16      min_height;
    Q16_16      max_height;
    Q16_16      min_humidity;
    Q16_16      max_humidity;
} BiomeType;

FieldId dbiome_field_biome_id(void);

bool          dbiome_register_type(const BiomeType *type);
const BiomeType *dbiome_get_type(BiomeId id);

BiomeId dbiome_get_at_tile(BodyId body, const WPosTile *tile);
BiomeId dbiome_classify(BodyId body, TempK temp, Q16_16 precip, Q16_16 humidity, Q16_16 height_m);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DBIOME_H */
