#ifndef DOMINO_DORBIT_H
#define DOMINO_DORBIT_H

#include "dnumeric.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t BodyId;     /* star, planet, moon, station central bodies */
typedef uint32_t SpaceSiteId;

typedef struct {
    Q48_16 x; /* metres, inertial frame */
    Q48_16 y;
    Q48_16 z;
} SpacePos;

typedef struct {
    BodyId   central;   /* central body */
    Q48_16   a;         /* semi-major axis [m], Q48.16 */
    Q16_16   e;         /* eccentricity in [0..1) */
    Turn     i;         /* inclination */
    Turn     Omega;     /* longitude of ascending node */
    Turn     omega;     /* argument of periapsis */
    Turn     M0;        /* mean anomaly at t0 (turns) */
    U64      t0;        /* epoch in simulation seconds */

    /* optional linear drifts */
    Turn     dOmega_dt; /* turns per second */
    Turn     domega_dt; /* turns per second */
    Q16_16   da_dt;     /* metres per second, Q16.16 */
    Q16_16   de_dt;     /* per second */
    Turn     di_dt;     /* turns per second */
} OrbitComponent;

/* Kepler helpers (integer/fixed only) */

Turn    dorbit_mean_anomaly(const OrbitComponent *orb, U64 t);
Turn    dorbit_solve_kepler(Turn mean_anomaly, Q16_16 e);
Turn    dorbit_true_anomaly(Turn eccentric_anomaly, Q16_16 e);
void    dorbit_position_in_orbital_plane(Q48_16 a, Q16_16 e, Turn true_anom, SpacePos *out);
void    dorbit_to_space_pos(const OrbitComponent *orb, U64 t, SpacePos *out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DORBIT_H */
