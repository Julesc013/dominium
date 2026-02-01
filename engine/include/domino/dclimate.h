/*
FILE: include/domino/dclimate.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dclimate
RESPONSIBILITY: Defines the public contract for `dclimate` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DCLIMATE_H
#define DOMINO_DCLIMATE_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dworld.h"
#include "dfield.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ClimateGrid: Public type used by `dclimate`. */
typedef struct {
    BodyId   body;
    U32      width;
    U32      height;
    TempK   *mean_temp_K;   /* per cell */
    Q16_16  *mean_precip;   /* arbitrary units */
    Q16_16  *mean_humidity; /* 0..1 */
} ClimateGrid;

/* Field handles (registered via dfield) */
FieldId dclimate_field_mean_temp(void);
/* Purpose: Field mean precip.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
FieldId dclimate_field_mean_precip(void);
/* Purpose: Field mean humidity.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
FieldId dclimate_field_mean_humidity(void);

/* Grid lifecycle */
bool        dclimate_init_grid(BodyId body, U32 width, U32 height, Q16_16 albedo, Q16_16 greenhouse_factor);
/* Purpose: Get grid.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
ClimateGrid *dclimate_get_grid(BodyId body);

/* Sampling */
bool dclimate_sample_at_tile(BodyId body, const WPosTile *tile, TempK *out_temp_K, Q16_16 *out_precip, Q16_16 *out_humidity);
/* Purpose: Sample at lat lon.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dclimate_sample_at_lat_lon(BodyId body, Turn lat, Turn lon, Q16_16 height_m, TempK *out_temp_K, Q16_16 *out_precip, Q16_16 *out_humidity);

/* Direct cell set for offline/authoring overrides */
bool dclimate_set_cell(BodyId body, U32 gx, U32 gy, TempK temp_K, Q16_16 precip, Q16_16 humidity);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DCLIMATE_H */
