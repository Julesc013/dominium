/*
FILE: source/domino/render/api/core/dom_camera.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_camera
RESPONSIBILITY: Defines internal contract for `dom_camera`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CAMERA_H
#define DOM_CAMERA_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef dom_u32 dom_camera_id;
#define DOM_CAMERA_ID_INVALID ((dom_camera_id)0u)

typedef enum dom_camera_type_e {
    DOM_CAMERA_TYPE_TOPDOWN_2D = 0,
    DOM_CAMERA_TYPE_FIRSTPERSON_3D = 1
} dom_camera_type;

typedef struct dom_camera_2d_s {
    dom_i64 world_x_q32_32;
    dom_i64 world_y_q32_32;
    dom_i32 zoom_q16_16; /* pixels per metre */
} dom_camera_2d;

typedef struct dom_camera_3d_s {
    dom_i64 pos_x_q32_32;
    dom_i64 pos_y_q32_32;
    dom_i64 pos_z_q32_32;
    dom_i32 yaw_q16_16;
    dom_i32 pitch_q16_16;
    dom_i32 fov_y_q16_16;
    dom_i32 near_mm;
    dom_i32 far_mm;
} dom_camera_3d;

typedef struct dom_camera_s {
    dom_camera_type type;
    dom_camera_2d cam2d;
    dom_camera_3d cam3d;
} dom_camera;

dom_camera_id dom_camera_create(dom_camera_type type);
dom_err_t     dom_camera_destroy(dom_camera_id id);
dom_camera   *dom_camera_lookup(dom_camera_id id);

#ifdef __cplusplus
}
#endif

#endif /* DOM_CAMERA_H */
