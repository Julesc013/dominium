/*
FILE: include/dominium/environment.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / environment
RESPONSIBILITY: Defines the public contract for `environment` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_ENVIRONMENT_H
#define DOMINIUM_ENVIRONMENT_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "domino/dworld.h"
#include "dominium/world.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_environment_system: Public type used by `environment`. */
typedef struct dom_environment_system dom_environment_system;

/* dom_environment_desc: Public type used by `environment`. */
typedef struct dom_environment_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_environment_desc;

/* dom_environment_sample: Public type used by `environment`. */
typedef struct dom_environment_sample {
    uint32_t struct_size;
    uint32_t struct_version;
    int32_t  temperature_mK;
    uint32_t pressure_mPa;
    uint32_t humidity_permille;
    uint32_t wind_mm_s;
    uint32_t radiation_uSvph;
} dom_environment_sample;

/* Purpose: Create environment.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_environment_create(const dom_environment_desc* desc,
                                  dom_environment_system** out_env);
/* Purpose: Destroy environment.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void       dom_environment_destroy(dom_environment_system* env);
/* Purpose: Tick environment.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_environment_tick(dom_environment_system* env,
                                uint32_t dt_millis);
/* Purpose: Sample point.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_environment_sample_point(dom_environment_system* env,
                                        dom_surface_id surface,
                                        const WPosExact* pos,
                                        dom_environment_sample* out_sample,
                                        size_t out_sample_size);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_ENVIRONMENT_H */
