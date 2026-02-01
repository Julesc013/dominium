/*
FILE: include/domino/dbiome.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dbiome
RESPONSIBILITY: Defines the public contract for `dbiome` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DBIOME_H
#define DOMINO_DBIOME_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dworld.h"
#include "dfield.h"

#ifdef __cplusplus
extern "C" {
#endif

/* BiomeId: Identifier type for Biome objects in `dbiome`. */
typedef uint16_t BiomeId;

/* BiomeType: Public type used by `dbiome`. */
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

/* Purpose: Field biome id.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
FieldId dbiome_field_biome_id(void);

/* Purpose: Register type.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool          dbiome_register_type(const BiomeType *type);
/* Purpose: Get type.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const BiomeType *dbiome_get_type(BiomeId id);

/* Purpose: Get at tile.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
BiomeId dbiome_get_at_tile(BodyId body, const WPosTile *tile);
/* Purpose: Classify dbiome.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
BiomeId dbiome_classify(BodyId body, TempK temp, Q16_16 precip, Q16_16 humidity, Q16_16 height_m);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DBIOME_H */
