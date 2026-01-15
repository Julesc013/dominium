/*
FILE: source/domino/dorbit.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dorbit
RESPONSIBILITY: Implements `dorbit`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dorbit.h"
#include "domino/dnumeric.h"
#include "domino/dbody.h"

#include <limits.h>

#define DORBIT_MAX_ITER 8

/* constants in Q16.16 */
#define DORBIT_RAD_PER_TURN_Q16 ((Q16_16)411775)  /* 2*pi * 65536 */
#define DORBIT_TURN_PER_RAD_Q16 ((Q16_16)10430)   /* 1/(2*pi) * 65536 */
#define DORBIT_PI_OVER_TWO_TURN ((Turn)(1 << 15)) /* 0.5 turn = pi rad */
#define DORBIT_PI_TURN          ((Turn)(1 << 16)) /* 1 turn = 2*pi rad */

typedef struct {
    Q48_16 a;
    Q16_16 e;
    Turn   i;
    Turn   Omega;
    Turn   omega;
    Turn   M0;
} OrbitEval;

static U64 dorbit_isqrt_u64(U64 v)
{
    U64 res = 0;
    U64 bit = (U64)1 << 62;
    while (bit > v) {
        bit >>= 2;
    }
    while (bit != 0) {
        if (v >= res + bit) {
            v -= res + bit;
            res = (res >> 1) + bit;
        } else {
            res >>= 1;
        }
        bit >>= 2;
    }
    return res;
}

static Q16_16 dorbit_turn_to_rad_q16(Turn t)
{
    return (Q16_16)(((I64)t * (I64)DORBIT_RAD_PER_TURN_Q16) >> 16);
}

static Q16_16 dorbit_sin_turn(Turn t)
{
    Q16_16 x;
    I64 x2;
    I64 x3;
    Q16_16 res;
    /* reduce to [-0.5,0.5) turns */
    Turn tn = dnum_turn_normalise_neg_pos_half(t);
    x = dorbit_turn_to_rad_q16(tn);
    x2 = ((I64)x * (I64)x) >> 16;
    x3 = (x2 * (I64)x) >> 16;
    res = (Q16_16)((I64)x - (x3 / 6));
    return res;
}

static Q16_16 dorbit_cos_turn(Turn t)
{
    Q16_16 x;
    I64 x2;
    Q16_16 res;
    Turn tn = dnum_turn_normalise_neg_pos_half(t);
    x = dorbit_turn_to_rad_q16(tn);
    x2 = ((I64)x * (I64)x) >> 16;
    res = (Q16_16)((Q16_16)(1 << 16) - (Q16_16)(x2 / 2));
    return res;
}

static Q16_16 dorbit_q16_mul(Q16_16 a, Q16_16 b)
{
    return (Q16_16)(((I64)a * (I64)b) >> 16);
}

static Q48_16 dorbit_q48_mul_q16(Q48_16 a, Q16_16 b)
{
    return (Q48_16)(((I64)a * (I64)b) >> 16);
}

static Turn dorbit_atan_approx_turn(Q16_16 r_q16)
{
    /* atan(x) ≈ x*(pi/4 + 0.273*(1-|x|)) in radians, convert to turns */
    const Q16_16 PI_OVER_4_RAD_Q16 = (Q16_16)51472;
    const Q16_16 K_Q16 = (Q16_16)17826; /* 0.273 * 65536 */
    Q16_16 abs_r = (r_q16 < 0) ? (Q16_16)(-r_q16) : r_q16;
    Q16_16 one_minus = (Q16_16)((1 << 16) - abs_r);
    Q16_16 term = (Q16_16)(((I64)K_Q16 * (I64)one_minus) >> 16);
    Q16_16 base = (Q16_16)(PI_OVER_4_RAD_Q16 + term);
    Q16_16 angle_rad_q16 = (Q16_16)(((I64)r_q16 * (I64)base) >> 16);
    return (Turn)(((I64)angle_rad_q16 * (I64)DORBIT_TURN_PER_RAD_Q16) >> 16);
}

static Turn dorbit_atan2_turn(Q16_16 y, Q16_16 x)
{
    Q16_16 abs_y = (y < 0) ? (Q16_16)(-y) : y;
    Q16_16 abs_x = (x < 0) ? (Q16_16)(-x) : x;
    Turn angle = 0;
    if (x == 0 && y == 0) {
        return 0;
    }
    if (abs_x > abs_y) {
        Q16_16 r = (Q16_16)(((I64)y << 16) / (I64)x);
        angle = dorbit_atan_approx_turn(r);
        if (x < 0) {
            angle = (Turn)(angle + (Turn)0x8000); /* add 0.5 turn */
        }
    } else {
        Q16_16 r = (Q16_16)(((I64)x << 16) / (I64)y);
        angle = dorbit_atan_approx_turn(r);
        angle = (Turn)((Turn)0x4000 - angle); /* 0.25 turn - angle */
        if (y < 0) {
            angle = (Turn)(angle + (Turn)0x8000); /* add 0.5 turn */
        }
    }
    return dnum_turn_normalise_0_1(angle);
}

static Q16_16 dorbit_sqrt_q16(Q16_16 v)
{
    if (v <= 0) return 0;
    return (Q16_16)(dorbit_isqrt_u64((U64)v << 16));
}

static void dorbit_apply_drifts(const OrbitComponent *orb, I64 dt_s, OrbitEval *out_eval)
{
    if (!orb || !out_eval) return;
    out_eval->a = (Q48_16)((I64)orb->a + ((I64)orb->da_dt * dt_s));
    if (out_eval->a <= 0) {
        out_eval->a = (Q48_16)1;
    }

    out_eval->e = (Q16_16)((I64)orb->e + ((I64)orb->de_dt * dt_s));
    if (out_eval->e < 0) out_eval->e = 0;
    if (out_eval->e >= (Q16_16)(1 << 16)) out_eval->e = (Q16_16)((1 << 16) - 1);

    out_eval->i = dnum_turn_normalise_0_1((Turn)((I64)orb->i + ((I64)orb->di_dt * dt_s)));
    out_eval->Omega = dnum_turn_normalise_0_1((Turn)((I64)orb->Omega + ((I64)orb->dOmega_dt * dt_s)));
    out_eval->omega = dnum_turn_normalise_0_1((Turn)((I64)orb->omega + ((I64)orb->domega_dt * dt_s)));
    out_eval->M0 = orb->M0;
}

static Turn dorbit_mean_motion_turns(const OrbitEval *eval, Q48_16 mu)
{
    I64 a_m;
    I64 mu_m;
    I64 denom;
    I64 ratio;
    U64 sqrt_r;
    Q16_16 sqrt_q16;
    if (!eval) return 0;
    if (mu == 0) return 0;
    a_m = (I64)(eval->a >> 16);
    mu_m = (I64)(mu >> 16);
    if (a_m <= 0 || mu_m <= 0) return 0;

    /* scale down a to keep a^3 in range */
    {
        int shift = 0;
        while (a_m > 1000000 && shift < 10) {
            a_m >>= 1;
            shift++;
        }
        denom = a_m * a_m;
        if (denom == 0 || (a_m != 0 && denom / a_m != a_m)) {
            return 0;
        }
        denom = denom * a_m;
        if (denom == 0) return 0;

        ratio = mu_m;
        if (shift > 0) {
            int boost = shift * 3;
            while (boost > 0 && ratio < (I64)(LLONG_MAX / 2)) {
                ratio <<= 1;
                boost--;
            }
        }
    }

    ratio = ratio / denom;
    if (ratio <= 0) return 0;
    sqrt_r = dorbit_isqrt_u64((U64)ratio);
    sqrt_q16 = (Q16_16)(sqrt_r << 16);
    return (Turn)(((I64)sqrt_q16 * (I64)DORBIT_TURN_PER_RAD_Q16) >> 16);
}

Turn dorbit_mean_anomaly(const OrbitComponent *orb, U64 t)
{
    I64 dt_s;
    OrbitEval eval;
    Q48_16 mu;
    Turn n;
    Turn delta;
    if (!orb) return 0;

    if (t >= orb->t0) dt_s = (I64)(t - orb->t0);
    else dt_s = -(I64)(orb->t0 - t);

    dorbit_apply_drifts(orb, dt_s, &eval);
    mu = dbody_get_mu(orb->central);
    n = dorbit_mean_motion_turns(&eval, mu);
    delta = (Turn)((I64)n * dt_s);
    return dnum_turn_normalise_0_1((Turn)((I64)eval.M0 + (I64)delta));
}

Turn dorbit_solve_kepler(Turn mean_anomaly, Q16_16 e)
{
    Turn E = dnum_turn_normalise_0_1(mean_anomaly);
    int iter;
    for (iter = 0; iter < DORBIT_MAX_ITER; ++iter) {
        Q16_16 sinE = dorbit_sin_turn(E);
        Q16_16 cosE = dorbit_cos_turn(E);
        Turn f = (Turn)((I32)E - (I32)mean_anomaly - (I32)(dorbit_q16_mul(e, sinE)));
        Q16_16 denom = (Q16_16)((1 << 16) - dorbit_q16_mul(e, cosE));
        if (denom == 0) break;
        E = (Turn)((I32)E - (I32)(((I64)f << 16) / denom));
    }
    return dnum_turn_normalise_0_1(E);
}

Turn dorbit_true_anomaly(Turn eccentric_anomaly, Q16_16 e)
{
    Q16_16 cosE = dorbit_cos_turn(eccentric_anomaly);
    Q16_16 sinE = dorbit_sin_turn(eccentric_anomaly);
    Q16_16 one_minus_e_cosE = (Q16_16)((1 << 16) - dorbit_q16_mul(e, cosE));
    Q16_16 sin_num;
    Q16_16 cos_num;
    Q16_16 sqrt_term;
    if (one_minus_e_cosE == 0) return 0;

    sqrt_term = dorbit_sqrt_q16((Q16_16)((1 << 16) - dorbit_q16_mul(e, e)));
    sin_num = dorbit_q16_mul(sqrt_term, sinE);
    cos_num = (Q16_16)(cosE - e);

    return dorbit_atan2_turn(
        (Q16_16)(((I64)sin_num << 16) / one_minus_e_cosE),
        (Q16_16)(((I64)cos_num << 16) / one_minus_e_cosE));
}

void dorbit_position_in_orbital_plane(Q48_16 a, Q16_16 e, Turn true_anom, SpacePos *out)
{
    Q16_16 cos_v = dorbit_cos_turn(true_anom);
    Q16_16 sin_v = dorbit_sin_turn(true_anom);
    Q16_16 one_minus_e2 = (Q16_16)((1 << 16) - dorbit_q16_mul(e, e));
    Q16_16 denom = (Q16_16)((1 << 16) + dorbit_q16_mul(e, cos_v));
    Q16_16 factor;
    Q48_16 r;
    if (!out) return;
    if (denom == 0) denom = 1;
    {
        I64 num = ((I64)one_minus_e2 << 16);
        if (num > (I64)INT32_MAX) num = (I64)INT32_MAX;
        factor = (Q16_16)(num / (I64)denom);
    }
    r = dorbit_q48_mul_q16(a, factor);
    out->x = dorbit_q48_mul_q16(r, cos_v);
    out->y = dorbit_q48_mul_q16(r, sin_v);
    out->z = 0;
}

void dorbit_to_space_pos(const OrbitComponent *orb, U64 t, SpacePos *out)
{
    I64 dt_s;
    OrbitEval eval;
    Q48_16 mu;
    Turn M;
    Turn E;
    Turn v;
    Turn u;
    Q16_16 cosO;
    Q16_16 sinO;
    Q16_16 cosi;
    Q16_16 sini;
    Q16_16 cosu;
    Q16_16 sinu;
    Q16_16 cos_v;
    Q16_16 one_minus_e2;
    Q16_16 denom;
    Q16_16 factor;
    Q48_16 r;
    Q48_16 x1;
    Q48_16 y1;
    if (!orb || !out) return;

    if (t >= orb->t0) dt_s = (I64)(t - orb->t0);
    else dt_s = -(I64)(orb->t0 - t);

    dorbit_apply_drifts(orb, dt_s, &eval);
    mu = dbody_get_mu(orb->central);

    M = dorbit_mean_anomaly(orb, t);
    E = dorbit_solve_kepler(M, eval.e);
    v = dorbit_true_anomaly(E, eval.e);
    u = dnum_turn_normalise_0_1((Turn)((I64)eval.omega + (I64)v));

    cosO = dorbit_cos_turn(eval.Omega);
    sinO = dorbit_sin_turn(eval.Omega);
    cosi = dorbit_cos_turn(eval.i);
    sini = dorbit_sin_turn(eval.i);
    cosu = dorbit_cos_turn(u);
    sinu = dorbit_sin_turn(u);
    cos_v = dorbit_cos_turn(v);

    one_minus_e2 = (Q16_16)((1 << 16) - dorbit_q16_mul(eval.e, eval.e));
    denom = (Q16_16)((1 << 16) + dorbit_q16_mul(eval.e, cos_v));
    if (denom == 0) denom = 1;
    {
        I64 num = ((I64)one_minus_e2 << 16);
        if (num > (I64)INT32_MAX) num = (I64)INT32_MAX;
        factor = (Q16_16)(num / (I64)denom);
    }
    r = dorbit_q48_mul_q16(eval.a, factor);
    x1 = dorbit_q48_mul_q16(r, cosu);
    y1 = dorbit_q48_mul_q16(r, sinu);

    /* Rotation from orbital plane to inertial */
    {
        Q16_16 sinO_cosi = dorbit_q16_mul(sinO, cosi);
        Q16_16 cosO_cosi = dorbit_q16_mul(cosO, cosi);
        out->x = dorbit_q48_mul_q16(x1, cosO) - dorbit_q48_mul_q16(y1, sinO_cosi);
        out->y = dorbit_q48_mul_q16(x1, sinO) + dorbit_q48_mul_q16(y1, cosO_cosi);
        out->z = dorbit_q48_mul_q16(y1, sini);
        /* TODO: clamp against overflow and refine rotation accuracy */
        (void)mu; /* reserved for future higher precision mean motion */
    }
}
