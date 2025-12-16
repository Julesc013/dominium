/*
FILE: source/domino/dvehicle.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dvehicle
RESPONSIBILITY: Implements `dvehicle`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dvehicle.h"
#include "domino/dnumeric.h"
#include "domino/dworld.h"

#include <string.h>

#define DVEHICLE_MAX             512
#define DVEHICLE_Q16_ONE         ((Q16_16)(1 << 16))
#define DVEHICLE_BASE_ACC        ((Q16_16)(1 << 12))  /* tiles/s^2 scaled */
#define DVEHICLE_SPACE_ACC       ((Q48_16)(1 << 20))  /* metres/s^2 scaled */
#define DVEHICLE_FRICTION_Q16    ((Q16_16)(256))      /* small drag per step */
#define DVEHICLE_MAX_SPEED_Q16   ((Q16_16)(6 << 16))
#define DVEHICLE_MAX_SPACE_SPEED ((Q48_16)(50LL << 32))

typedef struct {
    VehicleComponent comp;
    VehiclePose      pose;
    VelUnit          vel_x;
    VelUnit          vel_y;
    VelUnit          vel_z;
    Q48_16           vel_space_x;
    Q48_16           vel_space_y;
    Q48_16           vel_space_z;
    BodyId           body;
} VehicleState;

static VehicleState g_vehicles[DVEHICLE_MAX];
static bool         g_vehicle_used[DVEHICLE_MAX];
static VehicleId    g_vehicle_count = 0;

static Q16_16 dvehicle_mul_q16(Q16_16 a, Q16_16 b)
{
    return (Q16_16)(((I64)a * (I64)b) >> 16);
}

static Q16_16 dvehicle_abs_q16(Q16_16 v)
{
    return (v < 0) ? -v : v;
}

static Q48_16 dvehicle_abs_q48(Q48_16 v)
{
    return (v < 0) ? -v : v;
}

static Q16_16 dvehicle_clamp_q16(Q16_16 v, Q16_16 lo, Q16_16 hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static VehicleState *dvehicle_lookup(VehicleId id)
{
    U32 idx;
    if (id == 0) return 0;
    if (id > g_vehicle_count) return 0;
    idx = (U32)(id - 1);
    if (idx >= DVEHICLE_MAX) return 0;
    if (!g_vehicle_used[idx]) return 0;
    return &g_vehicles[idx];
}

static void dvehicle_init_pose(VehicleState *st, EnvironmentKind env)
{
    memset(&st->pose, 0, sizeof(st->pose));
    st->pose.env = env;
    st->body = 1; /* default body id, override via transition inputs later */
}

VehicleId dvehicle_register(AggregateId agg, EnvironmentKind env)
{
    U32 idx;
    VehicleState *st = 0;
    for (idx = 0; idx < DVEHICLE_MAX; ++idx) {
        if (!g_vehicle_used[idx]) {
            st = &g_vehicles[idx];
            g_vehicle_used[idx] = true;
            if (idx + 1 > g_vehicle_count) {
                g_vehicle_count = (VehicleId)(idx + 1);
            }
            break;
        }
    }
    if (!st) return 0;
    memset(st, 0, sizeof(*st));
    st->comp.id = (VehicleId)(idx + 1);
    st->comp.agg = agg;
    st->comp.env = env;
    dvehicle_init_pose(st, env);
    return st->comp.id;
}

VehicleComponent *dvehicle_get(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return 0;
    return &st->comp;
}

VehiclePose *dvehicle_get_pose(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return 0;
    return &st->pose;
}

bool dvehicle_set_pose(VehicleId id, const VehiclePose *pose)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st || !pose) return false;
    st->pose = *pose;
    st->comp.env = pose->env;
    return true;
}

bool dvehicle_set_controls(VehicleId id, Q16_16 throttle, Q16_16 yaw_cmd, Q16_16 pitch_cmd, Q16_16 roll_cmd)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    st->comp.throttle = throttle;
    st->comp.yaw_cmd = yaw_cmd;
    st->comp.pitch_cmd = pitch_cmd;
    st->comp.roll_cmd = roll_cmd;
    return true;
}

bool dvehicle_set_flags(VehicleId id, uint32_t flags)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    st->comp.flags = flags;
    return true;
}

static Turn dvehicle_cmd_turn_delta(Q16_16 cmd, Turn rate_per_tick, U32 ticks)
{
    I64 delta = ((I64)cmd * (I64)rate_per_tick * (I64)ticks) >> 16;
    return (Turn)delta;
}

static void dvehicle_integrate_orientation(VehicleComponent *comp, Orientation *ori, U32 ticks)
{
    const Turn yaw_rate = (Turn)(1 << 10);
    const Turn pitch_rate = (Turn)(1 << 11);
    const Turn roll_rate = (Turn)(1 << 11);
    if (!comp || !ori) return;
    ori->yaw = dnum_turn_add(ori->yaw, dvehicle_cmd_turn_delta(comp->yaw_cmd, yaw_rate, ticks));
    ori->pitch = dnum_turn_add(ori->pitch, dvehicle_cmd_turn_delta(comp->pitch_cmd, pitch_rate, ticks));
    ori->roll = dnum_turn_add(ori->roll, dvehicle_cmd_turn_delta(comp->roll_cmd, roll_rate, ticks));
}

static void dvehicle_heading_unit(Turn yaw, Q16_16 *out_x, Q16_16 *out_y)
{
    Turn norm = dnum_turn_normalise_0_1(yaw);
    Turn quarter = (Turn)(1 << 14); /* 0.25 turns */
    if (out_x) *out_x = 0;
    if (out_y) *out_y = 0;
    if (norm < quarter) {
        if (out_x) *out_x = DVEHICLE_Q16_ONE;
    } else if (norm < (Turn)(quarter * 2)) {
        if (out_y) *out_y = DVEHICLE_Q16_ONE;
    } else if (norm < (Turn)(quarter * 3)) {
        if (out_x) *out_x = (Q16_16)(-DVEHICLE_Q16_ONE);
    } else {
        if (out_y) *out_y = (Q16_16)(-DVEHICLE_Q16_ONE);
    }
}

static void dvehicle_integrate_pos(WPosExact *pos, VelUnit vx, VelUnit vy, VelUnit vz, U32 ticks)
{
    Q16_16 dt_ticks;
    PosUnit dx;
    PosUnit dy;
    PosUnit dz;
    if (!pos) return;
    dt_ticks = (Q16_16)(((I64)g_domino_dt_s * (I64)ticks));
    dx = dvehicle_mul_q16(vx, dt_ticks);
    dy = dvehicle_mul_q16(vy, dt_ticks);
    dz = dvehicle_mul_q16(vz, dt_ticks);

    pos->dx += dx;
    pos->dy += dy;
    pos->dz += dz;

    while (pos->dx >= DVEHICLE_Q16_ONE) {
        pos->dx -= DVEHICLE_Q16_ONE;
        pos->tile.x = dworld_wrap_tile_coord(pos->tile.x + 1);
    }
    while (pos->dx < 0) {
        pos->dx += DVEHICLE_Q16_ONE;
        pos->tile.x = dworld_wrap_tile_coord(pos->tile.x - 1);
    }
    while (pos->dy >= DVEHICLE_Q16_ONE) {
        pos->dy -= DVEHICLE_Q16_ONE;
        pos->tile.y = dworld_wrap_tile_coord(pos->tile.y + 1);
    }
    while (pos->dy < 0) {
        pos->dy += DVEHICLE_Q16_ONE;
        pos->tile.y = dworld_wrap_tile_coord(pos->tile.y - 1);
    }

    while (pos->dz >= DVEHICLE_Q16_ONE) {
        pos->dz -= DVEHICLE_Q16_ONE;
        pos->tile.z++;
    }
    while (pos->dz < 0) {
        pos->dz += DVEHICLE_Q16_ONE;
        pos->tile.z--;
    }
    if (pos->tile.z < (TileHeight)DOM_Z_MIN) pos->tile.z = (TileHeight)DOM_Z_MIN;
    if (pos->tile.z > (TileHeight)DOM_Z_MAX) pos->tile.z = (TileHeight)DOM_Z_MAX;
}

static void dvehicle_apply_drag(VelUnit *v)
{
    if (!v) return;
    *v = dvehicle_mul_q16(*v, (Q16_16)(DVEHICLE_Q16_ONE - DVEHICLE_FRICTION_Q16));
}

static void dvehicle_cap_speed(VelUnit *vx, VelUnit *vy, VelUnit *vz)
{
    Q16_16 mag;
    if (!vx || !vy) return;
    mag = dvehicle_abs_q16(*vx) + dvehicle_abs_q16(*vy);
    if (vz) mag += dvehicle_abs_q16(*vz);
    if (mag > DVEHICLE_MAX_SPEED_Q16 && mag != 0) {
        *vx = dvehicle_mul_q16(*vx, DVEHICLE_MAX_SPEED_Q16);
        *vy = dvehicle_mul_q16(*vy, DVEHICLE_MAX_SPEED_Q16);
        if (vz) *vz = dvehicle_mul_q16(*vz, DVEHICLE_MAX_SPEED_Q16);
        *vx = (VelUnit)((I64)(*vx) / mag);
        *vy = (VelUnit)((I64)(*vy) / mag);
        if (vz) *vz = (VelUnit)((I64)(*vz) / mag);
    }
}

static void dvehicle_cap_space_speed(VehicleState *st)
{
    Q48_16 mag;
    if (!st) return;
    mag = dvehicle_abs_q48(st->vel_space_x) + dvehicle_abs_q48(st->vel_space_y) + dvehicle_abs_q48(st->vel_space_z);
    if (mag > DVEHICLE_MAX_SPACE_SPEED && mag != 0) {
        st->vel_space_x = (Q48_16)(((I64)st->vel_space_x * (I64)DVEHICLE_MAX_SPACE_SPEED) / mag);
        st->vel_space_y = (Q48_16)(((I64)st->vel_space_y * (I64)DVEHICLE_MAX_SPACE_SPEED) / mag);
        st->vel_space_z = (Q48_16)(((I64)st->vel_space_z * (I64)DVEHICLE_MAX_SPACE_SPEED) / mag);
    }
}

static Q16_16 dvehicle_speed_xy(const VehicleState *st)
{
    if (!st) return 0;
    return (Q16_16)(dvehicle_abs_q16(st->vel_x) + dvehicle_abs_q16(st->vel_y));
}

bool dvehicle_step_surface(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    Q16_16 hx = 0;
    Q16_16 hy = 0;
    Q16_16 acc = 0;
    if (!st) return false;
    dvehicle_integrate_orientation(&st->comp, &st->pose.surface_or_air.ori, ticks);
    dvehicle_heading_unit(st->pose.surface_or_air.ori.yaw, &hx, &hy);
    acc = dvehicle_mul_q16(st->comp.throttle, DVEHICLE_BASE_ACC);
    acc = (Q16_16)((I64)acc * (I64)ticks);
    st->vel_x += dvehicle_mul_q16(acc, hx);
    st->vel_y += dvehicle_mul_q16(acc, hy);
    dvehicle_apply_drag(&st->vel_x);
    dvehicle_apply_drag(&st->vel_y);
    dvehicle_cap_speed(&st->vel_x, &st->vel_y, 0);
    dvehicle_integrate_pos(&st->pose.surface_or_air.pos, st->vel_x, st->vel_y, 0, ticks);
    st->pose.env = ENV_SURFACE_GRID;
    st->comp.env = ENV_SURFACE_GRID;
    return true;
}

bool dvehicle_step_water_surface(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    Q16_16 hx = 0;
    Q16_16 hy = 0;
    Q16_16 acc = 0;
    if (!st) return false;
    dvehicle_integrate_orientation(&st->comp, &st->pose.water.ori, ticks);
    dvehicle_heading_unit(st->pose.water.ori.yaw, &hx, &hy);
    acc = dvehicle_mul_q16(st->comp.throttle, DVEHICLE_BASE_ACC >> 1);
    acc = (Q16_16)((I64)acc * (I64)ticks);
    st->vel_x += dvehicle_mul_q16(acc, hx);
    st->vel_y += dvehicle_mul_q16(acc, hy);
    dvehicle_apply_drag(&st->vel_x);
    dvehicle_apply_drag(&st->vel_y);
    dvehicle_cap_speed(&st->vel_x, &st->vel_y, 0);
    dvehicle_integrate_pos(&st->pose.water.pos, st->vel_x, st->vel_y, 0, ticks);
    st->pose.env = ENV_WATER_SURFACE;
    st->comp.env = ENV_WATER_SURFACE;
    return true;
}

bool dvehicle_step_water_submerged(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    Q16_16 acc = 0;
    if (!st) return false;
    dvehicle_integrate_orientation(&st->comp, &st->pose.water.ori, ticks);
    acc = dvehicle_mul_q16(st->comp.throttle, DVEHICLE_BASE_ACC >> 1);
    acc = (Q16_16)((I64)acc * (I64)ticks);
    st->vel_z += dvehicle_mul_q16(acc, st->comp.pitch_cmd);
    dvehicle_apply_drag(&st->vel_x);
    dvehicle_apply_drag(&st->vel_y);
    dvehicle_apply_drag(&st->vel_z);
    dvehicle_cap_speed(&st->vel_x, &st->vel_y, &st->vel_z);
    dvehicle_integrate_pos(&st->pose.water.pos, st->vel_x, st->vel_y, st->vel_z, ticks);
    st->pose.env = ENV_WATER_SUBMERGED;
    st->comp.env = ENV_WATER_SUBMERGED;
    return true;
}

bool dvehicle_step_air_local(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    Q16_16 hx = 0;
    Q16_16 hy = 0;
    Q16_16 acc = 0;
    if (!st) return false;
    dvehicle_integrate_orientation(&st->comp, &st->pose.surface_or_air.ori, ticks);
    dvehicle_heading_unit(st->pose.surface_or_air.ori.yaw, &hx, &hy);
    acc = dvehicle_mul_q16(st->comp.throttle, DVEHICLE_BASE_ACC);
    acc = (Q16_16)((I64)acc * (I64)ticks);
    st->vel_x += dvehicle_mul_q16(acc, hx);
    st->vel_y += dvehicle_mul_q16(acc, hy);
    st->vel_z += dvehicle_mul_q16(acc, st->comp.pitch_cmd);
    dvehicle_apply_drag(&st->vel_x);
    dvehicle_apply_drag(&st->vel_y);
    dvehicle_apply_drag(&st->vel_z);
    dvehicle_cap_speed(&st->vel_x, &st->vel_y, &st->vel_z);
    dvehicle_integrate_pos(&st->pose.surface_or_air.pos, st->vel_x, st->vel_y, st->vel_z, ticks);
    st->pose.env = ENV_AIR_LOCAL;
    st->comp.env = ENV_AIR_LOCAL;
    return true;
}

bool dvehicle_step_high_atmo(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    Q16_16 climb = 0;
    if (!st) return false;
    dvehicle_integrate_orientation(&st->comp, &st->pose.high_atmo.ori, ticks);
    climb = dvehicle_mul_q16(st->comp.throttle, (Q16_16)(1 << 12));
    climb = (Q16_16)((I64)climb * (I64)ticks);
    st->pose.high_atmo.alt_m += climb;
    st->pose.high_atmo.lon = dnum_turn_add(st->pose.high_atmo.lon, dvehicle_cmd_turn_delta(st->comp.yaw_cmd, (Turn)(1 << 10), ticks));
    st->pose.high_atmo.lat = dnum_turn_add(st->pose.high_atmo.lat, dvehicle_cmd_turn_delta(st->comp.pitch_cmd, (Turn)(1 << 10), ticks));
    st->pose.env = ENV_HIGH_ATMO;
    st->comp.env = ENV_HIGH_ATMO;
    return true;
}

bool dvehicle_step_orbit(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    dvehicle_integrate_orientation(&st->comp, &st->pose.orbit.ori, ticks);
    st->pose.orbit.orbit.M0 = dnum_turn_add(st->pose.orbit.orbit.M0, dvehicle_cmd_turn_delta(st->comp.throttle, (Turn)(1 << 12), ticks));
    st->pose.env = ENV_ORBIT;
    st->comp.env = ENV_ORBIT;
    return true;
}

bool dvehicle_step_vacuum_local(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    Q48_16 acc;
    if (!st) return false;
    dvehicle_integrate_orientation(&st->comp, &st->pose.vacuum_local.ori, ticks);
    acc = (Q48_16)(((I64)st->comp.throttle * (I64)DVEHICLE_SPACE_ACC) >> 16);
    acc = (Q48_16)((I64)acc * (I64)ticks);
    st->vel_space_x += acc;
    dvehicle_cap_space_speed(st);
    st->pose.vacuum_local.pos.x += (Q48_16)((I64)st->vel_space_x * (I64)ticks);
    st->pose.vacuum_local.pos.y += (Q48_16)((I64)st->vel_space_y * (I64)ticks);
    st->pose.vacuum_local.pos.z += (Q48_16)((I64)st->vel_space_z * (I64)ticks);
    st->pose.env = ENV_VACUUM_LOCAL;
    st->comp.env = ENV_VACUUM_LOCAL;
    return true;
}

bool dvehicle_step(VehicleId id, U32 ticks)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    switch (st->comp.env) {
        case ENV_SURFACE_GRID:    return dvehicle_step_surface(id, ticks);
        case ENV_WATER_SURFACE:   return dvehicle_step_water_surface(id, ticks);
        case ENV_WATER_SUBMERGED: return dvehicle_step_water_submerged(id, ticks);
        case ENV_AIR_LOCAL:       return dvehicle_step_air_local(id, ticks);
        case ENV_HIGH_ATMO:       return dvehicle_step_high_atmo(id, ticks);
        case ENV_ORBIT:           return dvehicle_step_orbit(id, ticks);
        case ENV_VACUUM_LOCAL:    return dvehicle_step_vacuum_local(id, ticks);
        default:                  return false;
    }
}

/* Environment transitions */

static Turn dvehicle_tile_to_turn(TileCoord t)
{
    return (Turn)((((I64)dworld_wrap_tile_coord(t) & 0xFFFFFF) * (I64)DVEHICLE_Q16_ONE) >> DOM_WORLD_TILES_LOG2);
}

bool dvehicle_try_switch_surface_to_air(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    Q16_16 throttle_thr = (Q16_16)((3 * (I64)DVEHICLE_Q16_ONE) / 4);
    if (!st) return false;
    if (st->comp.env != ENV_SURFACE_GRID) return false;
    if (st->comp.throttle > throttle_thr && dvehicle_speed_xy(st) > (Q16_16)(1 << 14)) {
        st->comp.env = ENV_AIR_LOCAL;
        st->pose.env = ENV_AIR_LOCAL;
        st->pose.surface_or_air.pos.tile.z += 1;
        return true;
    }
    return false;
}

bool dvehicle_try_switch_air_to_high_atmo(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    Q16_16 alt_m;
    if (!st) return false;
    if (st->comp.env != ENV_AIR_LOCAL) return false;
    alt_m = dnum_from_int32((I32)st->pose.surface_or_air.pos.tile.z);
    if (alt_m > (Q16_16)((DOM_Z_BUILD_MAX + 128) << 16)) {
        st->comp.env = ENV_HIGH_ATMO;
        st->pose.env = ENV_HIGH_ATMO;
        st->pose.high_atmo.body = st->body;
        st->pose.high_atmo.alt_m = alt_m;
        st->pose.high_atmo.lat = dvehicle_tile_to_turn(st->pose.surface_or_air.pos.tile.y);
        st->pose.high_atmo.lon = dvehicle_tile_to_turn(st->pose.surface_or_air.pos.tile.x);
        st->pose.high_atmo.ori = st->pose.surface_or_air.ori;
        st->vel_x = st->vel_y = st->vel_z = 0;
        return true;
    }
    return false;
}

bool dvehicle_try_switch_high_atmo_to_orbit(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    if (st->comp.env != ENV_HIGH_ATMO) return false;
    if (st->pose.high_atmo.alt_m > (Q16_16)(2000 << 16)) {
        memset(&st->pose.orbit.orbit, 0, sizeof(st->pose.orbit.orbit));
        st->pose.orbit.orbit.central = st->body;
        st->pose.orbit.orbit.a = (Q48_16)((I64)st->pose.high_atmo.alt_m << 16);
        st->pose.orbit.orbit.e = 0;
        st->pose.orbit.orbit.i = 0;
        st->pose.orbit.orbit.M0 = 0;
        st->pose.orbit.ori = st->pose.high_atmo.ori;
        st->comp.env = ENV_ORBIT;
        st->pose.env = ENV_ORBIT;
        return true;
    }
    return false;
}

bool dvehicle_try_switch_orbit_to_high_atmo(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    if (st->comp.env != ENV_ORBIT) return false;
    if (st->pose.orbit.orbit.a < (Q48_16)((I64)(2500 << 16))) {
        st->pose.high_atmo.body = st->pose.orbit.orbit.central;
        st->pose.high_atmo.alt_m = (Q16_16)(st->pose.orbit.orbit.a >> 16);
        st->pose.high_atmo.lat = 0;
        st->pose.high_atmo.lon = 0;
        st->pose.high_atmo.ori = st->pose.orbit.ori;
        st->comp.env = ENV_HIGH_ATMO;
        st->pose.env = ENV_HIGH_ATMO;
        return true;
    }
    return false;
}

bool dvehicle_try_switch_high_atmo_to_air(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    if (st->comp.env != ENV_HIGH_ATMO) return false;
    if (st->pose.high_atmo.alt_m < (Q16_16)(256 << 16)) {
        st->pose.surface_or_air.pos.tile.x = dworld_wrap_tile_coord((TileCoord)(((I64)st->pose.high_atmo.lon * (I64)DOM_WORLD_TILES) >> 16));
        st->pose.surface_or_air.pos.tile.y = dworld_wrap_tile_coord((TileCoord)(((I64)st->pose.high_atmo.lat * (I64)DOM_WORLD_TILES) >> 16));
        st->pose.surface_or_air.pos.tile.z = DOM_Z_BUILD_MAX;
        st->pose.surface_or_air.pos.dx = 0;
        st->pose.surface_or_air.pos.dy = 0;
        st->pose.surface_or_air.pos.dz = 0;
        st->pose.surface_or_air.ori = st->pose.high_atmo.ori;
        st->vel_x = st->vel_y = st->vel_z = 0;
        st->comp.env = ENV_AIR_LOCAL;
        st->pose.env = ENV_AIR_LOCAL;
        return true;
    }
    return false;
}

bool dvehicle_try_switch_air_to_surface(VehicleId id)
{
    VehicleState *st = dvehicle_lookup(id);
    if (!st) return false;
    if (st->comp.env != ENV_AIR_LOCAL) return false;
    if (st->pose.surface_or_air.pos.tile.z <= DOM_Z_BUILD_MAX) {
        st->pose.surface_or_air.pos.tile.z = DOM_Z_BUILD_MAX;
        st->vel_z = 0;
        st->comp.env = ENV_SURFACE_GRID;
        st->pose.env = ENV_SURFACE_GRID;
        return true;
    }
    return false;
}

void dvehicle_tick_all(SimTick t, U32 ticks_per_call)
{
    U32 i;
    (void)t;
    if (ticks_per_call == 0) ticks_per_call = 1;
    for (i = 0; i < g_vehicle_count; ++i) {
        if (g_vehicle_used[i]) {
            dvehicle_step((VehicleId)(i + 1), ticks_per_call);
        }
    }
}
