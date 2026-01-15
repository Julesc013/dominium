/*
FILE: include/domino/dvehicle.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dvehicle
RESPONSIBILITY: Defines the public contract for `dvehicle` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DVEHICLE_H
#define DOMINO_DVEHICLE_H

#include "dnumeric.h"
#include "dworld.h"
#include "dorbit.h"
#include "daggregate.h"

#ifdef __cplusplus
extern "C" {
#endif

/* VehicleId: Identifier type for Vehicle objects in `dvehicle`. */
typedef uint32_t VehicleId;

/* Orientation: Public type used by `dvehicle`. */
typedef struct {
    Turn yaw;
    Turn pitch;
    Turn roll;
} Orientation;

/* VehicleComponent: Public type used by `dvehicle`. */
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

/* surface_or_air: Public type used by `dvehicle`. */
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
/* Purpose: Get dvehicle.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
VehicleComponent *dvehicle_get(VehicleId id);
/* Purpose: Get pose.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
VehiclePose     *dvehicle_get_pose(VehicleId id);
/* Purpose: Set pose.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool             dvehicle_set_pose(VehicleId id, const VehiclePose *pose);
/* Purpose: Set controls.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool             dvehicle_set_controls(VehicleId id, Q16_16 throttle, Q16_16 yaw_cmd, Q16_16 pitch_cmd, Q16_16 roll_cmd);
/* Purpose: Set flags.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool             dvehicle_set_flags(VehicleId id, uint32_t flags);

/* Per-env integrators (stubbed but deterministic) */
bool dvehicle_step_surface(VehicleId id, U32 ticks);
/* Purpose: Step water surface.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_step_water_surface(VehicleId id, U32 ticks);
/* Purpose: Step water submerged.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_step_water_submerged(VehicleId id, U32 ticks);
/* Purpose: Step air local.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_step_air_local(VehicleId id, U32 ticks);
/* Purpose: Step high atmo.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_step_high_atmo(VehicleId id, U32 ticks);
/* Purpose: Step orbit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_step_orbit(VehicleId id, U32 ticks);
/* Purpose: Step vacuum local.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_step_vacuum_local(VehicleId id, U32 ticks);

/* General dispatcher */
bool dvehicle_step(VehicleId id, U32 ticks);

/* Environment transitions (altitude/speed thresholds, stubbed) */
bool dvehicle_try_switch_surface_to_air(VehicleId id);
/* Purpose: Try switch air to high atmo.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_try_switch_air_to_high_atmo(VehicleId id);
/* Purpose: Try switch high atmo to orbit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_try_switch_high_atmo_to_orbit(VehicleId id);
/* Purpose: Try switch orbit to high atmo.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_try_switch_orbit_to_high_atmo(VehicleId id);
/* Purpose: Try switch high atmo to air.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_try_switch_high_atmo_to_air(VehicleId id);
/* Purpose: Try switch air to surface.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dvehicle_try_switch_air_to_surface(VehicleId id);

/* Bulk stepping */
void dvehicle_tick_all(SimTick t, U32 ticks_per_call);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DVEHICLE_H */
