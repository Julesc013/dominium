#ifndef DOMINO_DVEHICLE_H
#define DOMINO_DVEHICLE_H

#include <stdbool.h>
#include <stdint.h>

#include "dnumeric.h"
#include "dworld.h"
#include "dorbit.h"
#include "daggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t VehicleId;

typedef struct {
    Turn yaw;
    Turn pitch;
    Turn roll;
} Orientation;

typedef struct {
    VehicleId   id;
    AggregateId agg;
    EnvironmentKind env;

    /* control inputs */
    Q16_16 throttle;   /* -1..+1 */
    Q16_16 yaw_cmd;
    Q16_16 pitch_cmd;
    Q16_16 roll_cmd;

    /* autopilot / mode flags */
    uint32_t flags;
} VehicleComponent;

typedef struct {
    EnvironmentKind env;
    union {
        struct {
            WPosExact   pos;
            Orientation ori;
        } surface_or_air;

        struct {
            BodyId      body;
            Q16_16      alt_m;
            Turn        lat;
            Turn        lon;
            Orientation ori;
        } high_atmo;

        struct {
            OrbitComponent orbit;
            Orientation    ori;
        } orbit;

        struct {
            SpacePos    pos;
            Orientation ori;
        } vacuum_local;

        struct {
            WPosExact   pos;
            Orientation ori;
        } water;
    };
} VehiclePose;

/* Registry and lookup */
VehicleId        dvehicle_register(AggregateId agg, EnvironmentKind env);
VehicleComponent *dvehicle_get(VehicleId id);
VehiclePose     *dvehicle_get_pose(VehicleId id);
bool             dvehicle_set_pose(VehicleId id, const VehiclePose *pose);
bool             dvehicle_set_controls(VehicleId id, Q16_16 throttle, Q16_16 yaw_cmd, Q16_16 pitch_cmd, Q16_16 roll_cmd);
bool             dvehicle_set_flags(VehicleId id, uint32_t flags);

/* Per-env integrators (stubbed but deterministic) */
bool dvehicle_step_surface(VehicleId id, U32 ticks);
bool dvehicle_step_water_surface(VehicleId id, U32 ticks);
bool dvehicle_step_water_submerged(VehicleId id, U32 ticks);
bool dvehicle_step_air_local(VehicleId id, U32 ticks);
bool dvehicle_step_high_atmo(VehicleId id, U32 ticks);
bool dvehicle_step_orbit(VehicleId id, U32 ticks);
bool dvehicle_step_vacuum_local(VehicleId id, U32 ticks);

/* General dispatcher */
bool dvehicle_step(VehicleId id, U32 ticks);

/* Environment transitions (altitude/speed thresholds, stubbed) */
bool dvehicle_try_switch_surface_to_air(VehicleId id);
bool dvehicle_try_switch_air_to_high_atmo(VehicleId id);
bool dvehicle_try_switch_high_atmo_to_orbit(VehicleId id);
bool dvehicle_try_switch_orbit_to_high_atmo(VehicleId id);
bool dvehicle_try_switch_high_atmo_to_air(VehicleId id);
bool dvehicle_try_switch_air_to_surface(VehicleId id);

/* Bulk stepping */
void dvehicle_tick_all(SimTick t, U32 ticks_per_call);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DVEHICLE_H */
