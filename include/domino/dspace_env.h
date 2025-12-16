/*
FILE: include/domino/dspace_env.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dspace_env
RESPONSIBILITY: Defines the public contract for `dspace_env` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DSPACE_ENV_H
#define DOMINO_DSPACE_ENV_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dbody.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    BodyId   central;
    Q48_16   inner_radius_m;
    Q48_16   outer_radius_m;
    Turn     i;       /* belt plane inclination */
    Turn     Omega;   /* belt plane orientation */
    Q16_16   density; /* arbitrary units */
} BeltField;

typedef struct {
    BodyId   central;
    /* TODO: dipole/torus parameters */
} MagneticField;

/* Registration */
void      dspace_env_register_belt(const BeltField *belt);
void      dspace_env_register_magnetic(const MagneticField *mag);

/* Queries */
Q16_16    dspace_env_radiation_intensity(const SpacePos *pos);
Q16_16    dspace_env_belt_density(const SpacePos *pos);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DSPACE_ENV_H */
