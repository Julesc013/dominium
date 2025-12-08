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
