/*
FILE: include/domino/dfield.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dfield
RESPONSIBILITY: Defines the public contract for `dfield` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DFIELD_H
#define DOMINO_DFIELD_H

#include "dnumeric.h"
#include "dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

/* UnitKind: Enumeration/classifier for Unit in `dfield`. */
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

/* FieldStorageKind: Enumeration/classifier for Field Storage in `dfield`. */
typedef enum {
    FIELD_STORAGE_BOOL = 0,
    FIELD_STORAGE_U8,
    FIELD_STORAGE_Q4_12,
    FIELD_STORAGE_Q16_16,
} FieldStorageKind;

/* FieldId: Identifier type for Field objects in `dfield`. */
typedef uint16_t FieldId;

/* FieldDesc: Public type used by `dfield`. */
typedef struct {
    FieldId          id;
    const char      *name;
    UnitKind         unit;
    FieldStorageKind storage;
} FieldDesc;

/* Registration and lookup */

FieldId             dfield_register(const FieldDesc *def);
/* Purpose: Get dfield.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const FieldDesc    *dfield_get(FieldId id);
/* Purpose: Find by name.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const FieldDesc    *dfield_find_by_name(const char *name);

/* Encoding/decoding between runtime Q16.16 and storage types */
Q4_12   dfield_q16_to_q4(FieldId id, Q16_16 v);
/* Purpose: Q4 to q16.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Q16_16  dfield_q4_to_q16(FieldId id, Q4_12 raw);
/* Purpose: Q16 to u8.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
U8      dfield_q16_to_u8(FieldId id, Q16_16 v);
/* Purpose: U8 to q16.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Q16_16  dfield_u8_to_q16(FieldId id, U8 raw);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DFIELD_H */
