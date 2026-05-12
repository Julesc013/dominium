/*
FILE: source/dominium/game/runtime/dom_surface_height.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_height
RESPONSIBILITY: Deterministic procedural surface height sampler (stub v1).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_SURFACE_HEIGHT_H
#define DOM_SURFACE_HEIGHT_H

#include "domino/core/fixed.h"
#include "runtime/dom_surface_topology.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_SURFACE_HEIGHT_OK = 0,
    DOM_SURFACE_HEIGHT_ERR = -1,
    DOM_SURFACE_HEIGHT_INVALID_ARGUMENT = -2
};

/* Deterministic procedural height sample (stub).
 * Inputs:
 * - body_id: body identifier
 * - lat/long: Q16.16 turns
 * Output:
 * - height in meters (Q48.16)
 */
int dom_surface_height_sample(dom_body_id body_id,
                              const dom_topo_latlong_q16 *latlong,
                              q48_16 *out_height_m);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SURFACE_HEIGHT_H */
