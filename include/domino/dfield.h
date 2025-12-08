#ifndef DOMINO_DFIELD_H
#define DOMINO_DFIELD_H

#include "dnumeric.h"
#include "dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    UNIT_NONE = 0,
    UNIT_HEIGHT_M,        /* terrain height */
    UNIT_DEPTH_M,         /* water depth, depth below ref */
    UNIT_TEMP_K,          /* temperature */
    UNIT_PRESSURE_PA,     /* pressure */
    UNIT_FRACTION,        /* 0..1, generic */
    UNIT_DENSITY_KG_M3,   /* density field */
    UNIT_WIND_M_S,        /* wind speed component */
    UNIT_RADIATION_SV_S,  /* radiation dose rate */
    UNIT_POLLUTION,       /* pollution scalar */
    UNIT_NOISE,           /* noise level */
    /* extend as needed */
} UnitKind;

typedef enum {
    FIELD_STORAGE_BOOL = 0,
    FIELD_STORAGE_U8,
    FIELD_STORAGE_Q4_12,
    FIELD_STORAGE_Q16_16,
} FieldStorageKind;

typedef uint16_t FieldId;

typedef struct {
    FieldId          id;
    const char      *name;
    UnitKind         unit;
    FieldStorageKind storage;
} FieldDesc;

/* Registration and lookup */

FieldId             dfield_register(const FieldDesc *def);
const FieldDesc    *dfield_get(FieldId id);
const FieldDesc    *dfield_find_by_name(const char *name);

/* Encoding/decoding between runtime Q16.16 and storage types */
Q4_12   dfield_q16_to_q4(FieldId id, Q16_16 v);
Q16_16  dfield_q4_to_q16(FieldId id, Q4_12 raw);
U8      dfield_q16_to_u8(FieldId id, Q16_16 v);
Q16_16  dfield_u8_to_q16(FieldId id, U8 raw);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DFIELD_H */
