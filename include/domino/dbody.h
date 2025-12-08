#ifndef DOMINO_DBODY_H
#define DOMINO_DBODY_H

#include "dnumeric.h"
#include "dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    BodyId     id;
    const char *name;
    MassKg     mass;
    Q48_16     radius_m;
    TempK      base_temp_K;
    Turn       axial_tilt;
    Turn       spin_phase0;
    Q16_16     spin_rate_turns_per_s;
    Q48_16     mu;          /* gravitational parameter [m^3/s^2], Q48.16 */
    OrbitComponent orbit;   /* orbit around central; central==self for root */
} Body;

typedef struct {
    SpaceSiteId id;
    const char *name;
    BodyId      attached_body;   /* 0 if free-floating */
    OrbitComponent orbit;        /* if orbiting */
    SpacePos    offset;          /* local offset from body-frame if attached */
} SpaceSite;

/* Body registry */
BodyId        dbody_register(const Body *def);
const Body   *dbody_get(BodyId id);
Q48_16        dbody_get_mu(BodyId id);
bool          dbody_get_space_pos(BodyId id, U64 t, SpacePos *out);

/* Solar helpers (assume a single primary star for now) */
void          dbody_sun_direction(BodyId body, U64 t, Q16_16 out_dir3[3]);
Q16_16        dbody_solar_flux_at_body(BodyId body);

/* Space site registry */
SpaceSiteId   dspace_site_register(const SpaceSite *def);
const SpaceSite *dspace_site_get(SpaceSiteId id);
bool          dspace_site_pos(SpaceSiteId id, U64 t, SpacePos *out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DBODY_H */
