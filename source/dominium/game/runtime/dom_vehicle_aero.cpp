/*
FILE: source/dominium/game/runtime/dom_vehicle_aero.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/vehicle_aero
RESPONSIBILITY: Deterministic aero properties/state and drag/heating update helpers.
*/
#include "runtime/dom_vehicle_aero.h"

#include <climits>

#include "domino/core/dom_deterministic_math.h"

namespace {

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

static u64 dom_u128_to_u64_clamp(const dom_u128 *value) {
    if (!value || value->hi != 0u) {
        return UINT64_MAX;
    }
    return value->lo;
}

static u64 mul_u64_clamp(u64 a, u64 b) {
    dom_u128 prod = dom_mul_u64(a, b);
    return dom_u128_to_u64_clamp(&prod);
}

static u64 add_u64_clamp(u64 a, u64 b) {
    if (UINT64_MAX - a < b) {
        return UINT64_MAX;
    }
    return a + b;
}

static i32 clamp_i64_to_i32(i64 v) {
    if (v > (i64)INT_MAX) {
        return INT_MAX;
    }
    if (v < (i64)INT_MIN) {
        return INT_MIN;
    }
    return (i32)v;
}

static u64 square_u64_clamp(i64 v) {
    u64 a = dom_abs_i64_u64(v);
    dom_u128 prod = dom_mul_u64(a, a);
    return dom_u128_to_u64_clamp(&prod);
}

static u64 speed_from_vel(const SpacePos *vel) {
    if (!vel) {
        return 0u;
    }
    i64 vx = d_q48_16_to_int(vel->x);
    i64 vy = d_q48_16_to_int(vel->y);
    i64 vz = d_q48_16_to_int(vel->z);
    u64 v2 = add_u64_clamp(square_u64_clamp(vx),
                           add_u64_clamp(square_u64_clamp(vy), square_u64_clamp(vz)));
    return dom_sqrt_u64(v2);
}

} // namespace

int dom_vehicle_aero_props_validate(const dom_vehicle_aero_props *props) {
    if (!props) {
        return DOM_VEHICLE_AERO_INVALID_ARGUMENT;
    }
    if (props->mass_kg_q16 <= 0) {
        return DOM_VEHICLE_AERO_INVALID_DATA;
    }
    if (props->drag_area_cda_q16 < 0 || props->heat_coeff_q16 < 0) {
        return DOM_VEHICLE_AERO_INVALID_DATA;
    }
    if (props->has_max_heat && props->max_heat_q16 <= 0) {
        return DOM_VEHICLE_AERO_INVALID_DATA;
    }
    return DOM_VEHICLE_AERO_OK;
}

void dom_vehicle_aero_state_reset(dom_vehicle_aero_state *state) {
    if (!state) {
        return;
    }
    state->heat_accum_q16 = 0;
    state->last_heating_rate_q16 = 0;
    state->last_drag_accel_q16 = 0;
}

int dom_vehicle_aero_apply(const dom_vehicle_aero_props *props,
                           const dom_media_sample *sample,
                           SpacePos *inout_vel,
                           dom_vehicle_aero_state *state) {
    if (!props || !sample || !inout_vel || !state) {
        return DOM_VEHICLE_AERO_INVALID_ARGUMENT;
    }
    if (dom_vehicle_aero_props_validate(props) != DOM_VEHICLE_AERO_OK) {
        return DOM_VEHICLE_AERO_INVALID_DATA;
    }

    if (sample->density_q16 <= 0) {
        state->last_drag_accel_q16 = 0;
        state->last_heating_rate_q16 = 0;
        return DOM_VEHICLE_AERO_OK;
    }

    u64 speed = speed_from_vel(inout_vel);
    if (speed == 0u) {
        state->last_drag_accel_q16 = 0;
        state->last_heating_rate_q16 = 0;
        return DOM_VEHICLE_AERO_OK;
    }

    u64 density = (u64)(u32)sample->density_q16;
    u64 cda = (u64)(u32)props->drag_area_cda_q16;
    u64 mass = (u64)(u32)props->mass_kg_q16;
    u64 heat_coeff = (u64)(u32)props->heat_coeff_q16;

    u64 v2 = mul_u64_clamp(speed, speed);
    u64 v3 = mul_u64_clamp(v2, speed);

    u64 drag_coeff_q16 = (mass == 0u) ? 0u : (mul_u64_clamp(density, cda) / mass);
    u64 drag_accel_q16 = mul_u64_clamp(drag_coeff_q16, v2);
    u64 heat_coeff_q16 = mul_u64_clamp(density, heat_coeff) >> 16;
    u64 heating_rate_q16 = mul_u64_clamp(heat_coeff_q16, v3);

    state->last_drag_accel_q16 = (q16_16)clamp_i64_to_i32((i64)drag_accel_q16);
    state->last_heating_rate_q16 = (q16_16)clamp_i64_to_i32((i64)heating_rate_q16);

    {
        i64 vx = d_q48_16_to_int(inout_vel->x);
        i64 vy = d_q48_16_to_int(inout_vel->y);
        i64 vz = d_q48_16_to_int(inout_vel->z);
        i64 denom = (i64)speed;

        i64 dvx_q16 = (denom != 0) ? ((vx * (i64)drag_accel_q16) / denom) : 0;
        i64 dvy_q16 = (denom != 0) ? ((vy * (i64)drag_accel_q16) / denom) : 0;
        i64 dvz_q16 = (denom != 0) ? ((vz * (i64)drag_accel_q16) / denom) : 0;

        inout_vel->x = d_q48_16_sub(inout_vel->x, d_q48_16_from_q16_16((q16_16)clamp_i64_to_i32(dvx_q16)));
        inout_vel->y = d_q48_16_sub(inout_vel->y, d_q48_16_from_q16_16((q16_16)clamp_i64_to_i32(dvy_q16)));
        inout_vel->z = d_q48_16_sub(inout_vel->z, d_q48_16_from_q16_16((q16_16)clamp_i64_to_i32(dvz_q16)));
    }

    {
        i64 heat = (i64)state->heat_accum_q16 + (i64)state->last_heating_rate_q16;
        state->heat_accum_q16 = (q16_16)clamp_i64_to_i32(heat);
        if (props->has_max_heat && state->heat_accum_q16 > props->max_heat_q16) {
            state->heat_accum_q16 = props->max_heat_q16;
        }
    }

    return DOM_VEHICLE_AERO_OK;
}
