/*
FILE: source/dominium/game/runtime/dom_orbit_lane.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/orbit_lane
RESPONSIBILITY: Orbit lane scaffolding and analytic event API (v1 patched conics).
*/
#include "runtime/dom_orbit_lane.h"

#include "domino/core/dom_deterministic_math.h"
#include "domino/core/fixed_math.h"

#include <limits.h>

enum {
    DOM_ORBIT_TAU_NUM = 6283185u,
    DOM_ORBIT_TAU_DEN = 1000000u,
    DOM_ORBIT_INV_TAU_Q16 = 10430
};

typedef struct dom_u128 {
    u64 hi;
    u64 lo;
} dom_u128;

static u64 dom_abs_i64_u64(i64 v) {
    if (v < 0) {
        if (v == (i64)LLONG_MIN) {
            return ((u64)1u) << 63u;
        }
        return (u64)(-v);
    }
    return (u64)v;
}

static dom_u128 dom_mul_u64(u64 a, u64 b) {
    u32 a0 = (u32)(a & 0xFFFFFFFFu);
    u32 a1 = (u32)(a >> 32);
    u32 b0 = (u32)(b & 0xFFFFFFFFu);
    u32 b1 = (u32)(b >> 32);

    u64 p0 = (u64)a0 * (u64)b0;
    u64 p1 = (u64)a0 * (u64)b1;
    u64 p2 = (u64)a1 * (u64)b0;
    u64 p3 = (u64)a1 * (u64)b1;

    u64 lo = p0;
    u64 carry = 0u;

    u64 t = lo + (p1 << 32);
    if (t < lo) {
        carry++;
    }
    lo = t;

    t = lo + (p2 << 32);
    if (t < lo) {
        carry++;
    }
    lo = t;

    dom_u128 result;
    result.hi = p3 + (p1 >> 32) + (p2 >> 32) + carry;
    result.lo = lo;
    return result;
}

static void dom_shift_right_u128(const dom_u128 *value,
                                 unsigned int shift,
                                 dom_u128 *out_value) {
    out_value->hi = value->hi >> shift;
    out_value->lo = (value->hi << (64u - shift)) | (value->lo >> shift);
}

static dom_u128 dom_add_u128(dom_u128 a, dom_u128 b) {
    dom_u128 out;
    out.lo = a.lo + b.lo;
    out.hi = a.hi + b.hi + (out.lo < a.lo ? 1u : 0u);
    return out;
}

static u64 dom_u128_to_u64_clamp(const dom_u128 *value) {
    if (!value || value->hi != 0u) {
        return UINT64_MAX;
    }
    return value->lo;
}

static dom_u128 dom_square_i64(i64 v) {
    u64 uv = dom_abs_i64_u64(v);
    return dom_mul_u64(uv, uv);
}

static dom_u128 dom_vec3_square_sum(i64 x, i64 y, i64 z) {
    dom_u128 sum = dom_add_u128(dom_square_i64(x), dom_square_i64(y));
    return dom_add_u128(sum, dom_square_i64(z));
}

static q48_16 dom_compose_signed_q48(u64 hi, u64 lo, d_bool negative) {
    if (!negative) {
        if (hi != 0u) {
            return (q48_16)LLONG_MAX;
        }
        if (lo > (u64)LLONG_MAX) {
            return (q48_16)LLONG_MAX;
        }
        return (q48_16)lo;
    }
    if (hi != 0u) {
        return (q48_16)LLONG_MIN;
    }
    if (lo > (((u64)1u) << 63u)) {
        return (q48_16)LLONG_MIN;
    }
    if (lo == (((u64)1u) << 63u)) {
        return (q48_16)LLONG_MIN;
    }
    return (q48_16)(-((i64)lo));
}

static q48_16 dom_mul_q48_q16(q48_16 a, q16_16 b) {
    return d_q48_16_mul(a, d_q48_16_from_q16_16(b));
}

static q48_16 dom_div_q48_q16(q48_16 a, q16_16 b) {
    return d_q48_16_div(a, d_q48_16_from_q16_16(b));
}

static q48_16 dom_mul_q48_q32(q48_16 a, q32_32 b) {
    d_bool negative = ((a < 0) != (b < 0)) ? D_TRUE : D_FALSE;
    u64 ua = dom_abs_i64_u64(a);
    u64 ub = dom_abs_i64_u64(b);

    dom_u128 prod = dom_mul_u64(ua, ub);
    dom_u128 scaled;
    dom_shift_right_u128(&prod, 32u, &scaled);

    return dom_compose_signed_q48(scaled.hi, scaled.lo, negative);
}

static q16_16 dom_orbit_kepler_solve(q16_16 mean_anomaly, q16_16 e) {
    q16_16 ecc_anomaly = mean_anomaly;
    q16_16 one = d_q16_16_from_int(1);

    for (int i = 0; i < 6; ++i) {
        q16_16 sin_e = dom_sin_q16(ecc_anomaly);
        q16_16 cos_e = dom_cos_q16(ecc_anomaly);
        q16_16 e_sin = d_q16_16_mul(e, sin_e);
        q16_16 e_cos = d_q16_16_mul(e, cos_e);
        q16_16 term = d_q16_16_mul(e_sin, (q16_16)DOM_ORBIT_INV_TAU_Q16);

        q16_16 f = d_q16_16_sub(d_q16_16_sub(ecc_anomaly, mean_anomaly), term);
        q16_16 denom = d_q16_16_sub(one, e_cos);
        q16_16 delta = d_q16_16_div(f, denom);

        ecc_anomaly = d_q16_16_sub(ecc_anomaly, delta);
    }

    return dom_angle_normalize_q16(ecc_anomaly);
}

static q16_16 dom_orbit_fraction_q16(u64 numer, u64 denom) {
    if (denom == 0u) {
        return 0;
    }
    if (numer >= denom) {
        numer = numer % denom;
    }
    unsigned int shift = 0u;
    while (numer > (UINT64_MAX >> 16) && shift < 16u && denom > 1u) {
        numer >>= 1u;
        denom >>= 1u;
        shift++;
    }
    if (denom == 0u) {
        return 0;
    }
    return (q16_16)((numer << 16) / denom);
}

static int dom_orbit_mean_anomaly_at_tick(const dom_orbit_state *orbit,
                                          dom_tick tick,
                                          q16_16 *out_mean_anomaly,
                                          dom_tick *out_period_ticks) {
    if (!orbit || !out_mean_anomaly || !out_period_ticks) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (dom_orbit_period_ticks(orbit, out_period_ticks) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (*out_period_ticks == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    i64 delta = (i64)tick - (i64)orbit->epoch_tick;
    i64 rem = 0;
    if (delta >= 0) {
        rem = (i64)((u64)delta % (*out_period_ticks));
    } else {
        rem = delta % (i64)(*out_period_ticks);
        if (rem < 0) {
            rem += (i64)(*out_period_ticks);
        }
    }

    q16_16 delta_frac = dom_orbit_fraction_q16((u64)rem, *out_period_ticks);
    *out_mean_anomaly = dom_angle_normalize_q16(
        (q16_16)(orbit->mean_anomaly_at_epoch + delta_frac));

    return DOM_ORBIT_LANE_OK;
}

static dom_tick dom_orbit_ticks_from_turns(dom_tick period_ticks, q16_16 delta_turns) {
    u64 dt = (u64)(u32)delta_turns;
    u64 period_hi = period_ticks >> 16;
    u64 period_lo = period_ticks & 0xFFFFu;
    u64 hi = 0u;

    if (period_hi != 0u) {
        if (dt > (UINT64_MAX / period_hi)) {
            return UINT64_MAX;
        }
        hi = period_hi * dt;
    }

    u64 lo = (period_lo * dt) >> 16;
    if (UINT64_MAX - hi < lo) {
        return UINT64_MAX;
    }
    return hi + lo;
}

int dom_orbit_state_validate(const dom_orbit_state *orbit) {
    if (!orbit) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (orbit->ups == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (orbit->mu_m3_s2 == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (orbit->semi_major_axis_m <= 0) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (orbit->eccentricity < 0) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (orbit->eccentricity >= d_q16_16_from_int(1)) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (orbit->soi_radius_m < 0) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    return DOM_ORBIT_LANE_OK;
}

int dom_orbit_elements_normalize(dom_orbit_state *orbit) {
    if (!orbit) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (dom_orbit_state_validate(orbit) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    orbit->inclination = dom_angle_normalize_q16(orbit->inclination);
    orbit->lon_ascending_node = dom_angle_normalize_q16(orbit->lon_ascending_node);
    orbit->arg_periapsis = dom_angle_normalize_q16(orbit->arg_periapsis);
    orbit->mean_anomaly_at_epoch = dom_angle_normalize_q16(orbit->mean_anomaly_at_epoch);
    return DOM_ORBIT_LANE_OK;
}

int dom_orbit_period_ticks(const dom_orbit_state *orbit,
                           dom_tick *out_period_ticks) {
    if (!orbit || !out_period_ticks) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (dom_orbit_state_validate(orbit) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    i64 a_m = d_q48_16_to_int(orbit->semi_major_axis_m);
    if (a_m <= 0) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    u64 a_m_u = (u64)a_m;
    u64 sqrt_a = dom_sqrt_u64(a_m_u);
    u64 sqrt_mu = dom_sqrt_u64(orbit->mu_m3_s2);
    if (sqrt_a == 0u || sqrt_mu == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    u64 numerator = 0u;
    if (a_m_u != 0u) {
        numerator = a_m_u * sqrt_a;
        if (numerator / a_m_u != sqrt_a) {
            numerator = UINT64_MAX;
        }
    }

    u64 root = numerator / sqrt_mu;
    if (root == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    u64 period_seconds = 0u;
    if (root > UINT64_MAX / DOM_ORBIT_TAU_NUM) {
        period_seconds = UINT64_MAX;
    } else {
        period_seconds = (root * DOM_ORBIT_TAU_NUM) / DOM_ORBIT_TAU_DEN;
    }
    if (period_seconds == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    if (period_seconds > (UINT64_MAX / orbit->ups)) {
        *out_period_ticks = UINT64_MAX;
    } else {
        *out_period_ticks = period_seconds * orbit->ups;
    }
    return DOM_ORBIT_LANE_OK;
}

int dom_orbit_eval_state(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_posvel *out_posvel) {
    if (!orbit || !out_posvel) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (dom_orbit_state_validate(orbit) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    dom_tick period_ticks = 0u;
    q16_16 mean_anomaly = 0;
    if (dom_orbit_mean_anomaly_at_tick(orbit, tick, &mean_anomaly, &period_ticks)
        != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    q16_16 ecc_anomaly = dom_orbit_kepler_solve(mean_anomaly, orbit->eccentricity);
    q16_16 sin_e = dom_sin_q16(ecc_anomaly);
    q16_16 cos_e = dom_cos_q16(ecc_anomaly);

    q16_16 e_cos = d_q16_16_mul(orbit->eccentricity, cos_e);
    q16_16 one = d_q16_16_from_int(1);
    q16_16 denom = d_q16_16_sub(one, e_cos);
    q16_16 cos_minus_e = d_q16_16_sub(cos_e, orbit->eccentricity);

    q16_16 e2 = d_q16_16_mul(orbit->eccentricity, orbit->eccentricity);
    q16_16 one_minus_e2 = d_q16_16_sub(one, e2);
    q16_16 sqrt_1_minus_e2 = d_fixed_sqrt_q16_16(one_minus_e2);

    q48_16 x_orb = dom_mul_q48_q16(orbit->semi_major_axis_m, cos_minus_e);
    q16_16 y_term = d_q16_16_mul(sqrt_1_minus_e2, sin_e);
    q48_16 y_orb = dom_mul_q48_q16(orbit->semi_major_axis_m, y_term);

    q16_16 cos_arg = dom_cos_q16(orbit->arg_periapsis);
    q16_16 sin_arg = dom_sin_q16(orbit->arg_periapsis);
    q16_16 cos_inc = dom_cos_q16(orbit->inclination);
    q16_16 sin_inc = dom_sin_q16(orbit->inclination);
    q16_16 cos_lon = dom_cos_q16(orbit->lon_ascending_node);
    q16_16 sin_lon = dom_sin_q16(orbit->lon_ascending_node);

    q48_16 x1 = d_q48_16_sub(dom_mul_q48_q16(x_orb, cos_arg),
                             dom_mul_q48_q16(y_orb, sin_arg));
    q48_16 y1 = d_q48_16_add(dom_mul_q48_q16(x_orb, sin_arg),
                             dom_mul_q48_q16(y_orb, cos_arg));
    q48_16 x2 = x1;
    q48_16 y2 = dom_mul_q48_q16(y1, cos_inc);
    q48_16 z2 = dom_mul_q48_q16(y1, sin_inc);

    q48_16 x3 = d_q48_16_sub(dom_mul_q48_q16(x2, cos_lon),
                             dom_mul_q48_q16(y2, sin_lon));
    q48_16 y3 = d_q48_16_add(dom_mul_q48_q16(x2, sin_lon),
                             dom_mul_q48_q16(y2, cos_lon));
    q48_16 z3 = z2;

    out_posvel->pos.x = x3;
    out_posvel->pos.y = y3;
    out_posvel->pos.z = z3;

    if (denom == 0) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    q32_32 factor_q32 = 0;
    if (period_ticks <= (UINT64_MAX / DOM_ORBIT_TAU_DEN)) {
        u64 factor_num = ((u64)DOM_ORBIT_TAU_NUM * (u64)orbit->ups);
        u64 factor_den = (DOM_ORBIT_TAU_DEN * period_ticks);
        if (factor_den != 0u && factor_num <= (UINT64_MAX >> 32)) {
            factor_q32 = (q32_32)((factor_num << 32) / factor_den);
        }
    }

    q48_16 vx_num = dom_mul_q48_q32(dom_mul_q48_q16(orbit->semi_major_axis_m, sin_e),
                                    factor_q32);
    q48_16 vy_term = dom_mul_q48_q16(orbit->semi_major_axis_m,
                                     d_q16_16_mul(sqrt_1_minus_e2, cos_e));
    q48_16 vy_num = dom_mul_q48_q32(vy_term, factor_q32);

    q48_16 vx_orb = dom_div_q48_q16(vx_num, denom);
    q48_16 vy_orb = dom_div_q48_q16(vy_num, denom);
    vx_orb = (q48_16)(-vx_orb);

    q48_16 vx1 = d_q48_16_sub(dom_mul_q48_q16(vx_orb, cos_arg),
                              dom_mul_q48_q16(vy_orb, sin_arg));
    q48_16 vy1 = d_q48_16_add(dom_mul_q48_q16(vx_orb, sin_arg),
                              dom_mul_q48_q16(vy_orb, cos_arg));
    q48_16 vx2 = vx1;
    q48_16 vy2 = dom_mul_q48_q16(vy1, cos_inc);
    q48_16 vz2 = dom_mul_q48_q16(vy1, sin_inc);

    q48_16 vx3 = d_q48_16_sub(dom_mul_q48_q16(vx2, cos_lon),
                              dom_mul_q48_q16(vy2, sin_lon));
    q48_16 vy3 = d_q48_16_add(dom_mul_q48_q16(vx2, sin_lon),
                              dom_mul_q48_q16(vy2, cos_lon));
    q48_16 vz3 = vz2;

    out_posvel->vel.x = vx3;
    out_posvel->vel.y = vy3;
    out_posvel->vel.z = vz3;

    return DOM_ORBIT_LANE_OK;
}

int dom_orbit_apply_maneuver(dom_orbit_state *orbit,
                             const dom_orbit_maneuver *maneuver) {
    dom_orbit_state prev;
    dom_orbit_posvel posvel;
    dom_tick period_ticks = 0u;
    q16_16 mean_anomaly = 0;
    i64 rx;
    i64 ry;
    i64 rz;
    i64 vx;
    i64 vy;
    i64 vz;
    u64 r2;
    u64 v2;
    u64 r_mag;
    u64 mu_over_r;
    u64 two_mu_over_r;
    u64 denom;
    u64 new_a;

    if (!orbit || !maneuver) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (dom_orbit_state_validate(orbit) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (maneuver->delta_v.x == 0 &&
        maneuver->delta_v.y == 0 &&
        maneuver->delta_v.z == 0) {
        return DOM_ORBIT_LANE_OK;
    }
    if (orbit->eccentricity != 0 || orbit->inclination != 0) {
        return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
    }

    prev = *orbit;
    if (dom_orbit_eval_state(&prev, maneuver->trigger_tick, &posvel) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    posvel.vel.x = d_q48_16_add(posvel.vel.x, maneuver->delta_v.x);
    posvel.vel.y = d_q48_16_add(posvel.vel.y, maneuver->delta_v.y);
    posvel.vel.z = d_q48_16_add(posvel.vel.z, maneuver->delta_v.z);

    rx = d_q48_16_to_int(posvel.pos.x);
    ry = d_q48_16_to_int(posvel.pos.y);
    rz = d_q48_16_to_int(posvel.pos.z);
    vx = d_q48_16_to_int(posvel.vel.x);
    vy = d_q48_16_to_int(posvel.vel.y);
    vz = d_q48_16_to_int(posvel.vel.z);

    {
        dom_u128 r2_sum = dom_vec3_square_sum(rx, ry, rz);
        dom_u128 v2_sum = dom_vec3_square_sum(vx, vy, vz);
        r2 = dom_u128_to_u64_clamp(&r2_sum);
        v2 = dom_u128_to_u64_clamp(&v2_sum);
    }
    r_mag = dom_sqrt_u64(r2);
    if (r_mag == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    mu_over_r = orbit->mu_m3_s2 / r_mag;
    if (mu_over_r > (UINT64_MAX / 2u)) {
        return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
    }
    two_mu_over_r = mu_over_r * 2u;
    if (v2 >= two_mu_over_r) {
        return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
    }
    denom = two_mu_over_r - v2;
    if (denom == 0u) {
        return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
    }
    new_a = orbit->mu_m3_s2 / denom;
    if (new_a == 0u) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (dom_orbit_mean_anomaly_at_tick(&prev,
                                       maneuver->trigger_tick,
                                       &mean_anomaly,
                                       &period_ticks) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    orbit->semi_major_axis_m = d_q48_16_from_int((i64)new_a);
    orbit->eccentricity = 0;
    orbit->mean_anomaly_at_epoch = mean_anomaly;
    orbit->epoch_tick = maneuver->trigger_tick;
    return DOM_ORBIT_LANE_OK;
}

int dom_orbit_next_event(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_event_kind kind,
                         dom_tick *out_tick) {
    if (!orbit || !out_tick) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (dom_orbit_state_validate(orbit) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    dom_tick period_ticks = 0u;
    q16_16 mean_anomaly = 0;
    if (dom_orbit_mean_anomaly_at_tick(orbit, tick, &mean_anomaly, &period_ticks)
        != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }

    q16_16 target_turn = 0;
    switch (kind) {
        case DOM_ORBIT_EVENT_PERIAPSIS:
            target_turn = 0;
            break;
        case DOM_ORBIT_EVENT_APOAPSIS:
            target_turn = (q16_16)0x8000;
            break;
        case DOM_ORBIT_EVENT_SOI_ENTER:
        case DOM_ORBIT_EVENT_SOI_EXIT:
            if (orbit->soi_radius_m <= 0) {
                return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
            }
            return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
        case DOM_ORBIT_EVENT_ASC_NODE:
        case DOM_ORBIT_EVENT_DESC_NODE:
            return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
        default:
            return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }

    q16_16 delta_turns = dom_angle_normalize_q16(
        (q16_16)(target_turn - mean_anomaly));
    dom_tick delta_ticks = dom_orbit_ticks_from_turns(period_ticks, delta_turns);

    if (UINT64_MAX - tick < delta_ticks) {
        *out_tick = UINT64_MAX;
    } else {
        *out_tick = tick + delta_ticks;
    }

    return DOM_ORBIT_LANE_OK;
}

int dom_orbit_next_any_event(const dom_orbit_state *orbit,
                             dom_tick tick,
                             dom_orbit_event_mask mask,
                             dom_orbit_event_kind *out_kind,
                             dom_tick *out_tick) {
    if (!orbit || !out_kind || !out_tick) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }
    if (dom_orbit_state_validate(orbit) != DOM_ORBIT_LANE_OK) {
        return DOM_ORBIT_LANE_INVALID_STATE;
    }
    if (mask == 0u) {
        return DOM_ORBIT_LANE_INVALID_ARGUMENT;
    }

    d_bool found = D_FALSE;
    dom_orbit_event_kind best_kind = DOM_ORBIT_EVENT_PERIAPSIS;
    dom_tick best_tick = 0u;

    for (u32 k = (u32)DOM_ORBIT_EVENT_PERIAPSIS;
         k <= (u32)DOM_ORBIT_EVENT_DESC_NODE;
         ++k) {
        dom_orbit_event_kind kind = (dom_orbit_event_kind)k;
        if ((mask & DOM_ORBIT_EVENT_MASK(kind)) == 0u) {
            continue;
        }
        dom_tick candidate_tick = 0u;
        int rc = dom_orbit_next_event(orbit, tick, kind, &candidate_tick);
        if (rc != DOM_ORBIT_LANE_OK) {
            continue;
        }
        if (!found || candidate_tick < best_tick ||
            (candidate_tick == best_tick && k < (u32)best_kind)) {
            found = D_TRUE;
            best_kind = kind;
            best_tick = candidate_tick;
        }
    }

    if (!found) {
        return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
    }

    *out_kind = best_kind;
    *out_tick = best_tick;
    return DOM_ORBIT_LANE_OK;
}
