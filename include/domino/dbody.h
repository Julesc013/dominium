/*
FILE: include/domino/dbody.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dbody
RESPONSIBILITY: Defines the public contract for `dbody` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DBODY_H
#define DOMINO_DBODY_H

#include "dnumeric.h"
#include "dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Body: Public type used by `dbody`. */
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

/* SpaceSite: Public type used by `dbody`. */
typedef struct {
    SpaceSiteId id;
    const char *name;
    BodyId      attached_body;   /* 0 if free-floating */
    OrbitComponent orbit;        /* if orbiting */
    SpacePos    offset;          /* local offset from body-frame if attached */
} SpaceSite;

/* Body registry */
BodyId        dbody_register(const Body *def);
/* Purpose: Get dbody.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const Body   *dbody_get(BodyId id);
/* Purpose: Get mu.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Q48_16        dbody_get_mu(BodyId id);
/* Purpose: Get space pos.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool          dbody_get_space_pos(BodyId id, U64 t, SpacePos *out);

/* Solar helpers (assume a single primary star for now) */
void          dbody_sun_direction(BodyId body, U64 t, Q16_16 out_dir3[3]);
/* Purpose: Solar flux at body.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Q16_16        dbody_solar_flux_at_body(BodyId body);

/* Space site registry */
SpaceSiteId   dspace_site_register(const SpaceSite *def);
/* Purpose: Get site.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const SpaceSite *dspace_site_get(SpaceSiteId id);
/* Purpose: Pos dspace site.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool          dspace_site_pos(SpaceSiteId id, U64 t, SpacePos *out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DBODY_H */
