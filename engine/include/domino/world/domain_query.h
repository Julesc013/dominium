/*
FILE: include/domino/world/domain_query.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/domain_query
RESPONSIBILITY: Defines deterministic domain query APIs and result metadata.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point, policy-driven resolution; conservative answers under uncertainty.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by DOMAIN1 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/arch/**`.
*/
#ifndef DOMINO_WORLD_DOMAIN_QUERY_H
#define DOMINO_WORLD_DOMAIN_QUERY_H

#include "domino/world/domain_volume.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_domain_query_status {
    DOM_DOMAIN_QUERY_OK = 0,
    DOM_DOMAIN_QUERY_REFUSED = 1
} dom_domain_query_status;

typedef enum dom_domain_confidence {
    DOM_DOMAIN_CONFIDENCE_EXACT = 0,
    DOM_DOMAIN_CONFIDENCE_LOWER_BOUND = 1,
    DOM_DOMAIN_CONFIDENCE_UNKNOWN = 2
} dom_domain_confidence;

typedef enum dom_domain_refusal_reason {
    DOM_DOMAIN_REFUSE_NONE = 0,
    DOM_DOMAIN_REFUSE_BUDGET = 1,
    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE = 2,
    DOM_DOMAIN_REFUSE_NO_SOURCE = 3,
    DOM_DOMAIN_REFUSE_NO_ANALYTIC = 4,
    DOM_DOMAIN_REFUSE_POLICY = 5,
    DOM_DOMAIN_REFUSE_INTERNAL = 6
} dom_domain_refusal_reason;

typedef struct dom_domain_budget {
    u32 max_units;
    u32 used_units;
} dom_domain_budget;

typedef struct dom_domain_query_meta {
    u32 status;         /* dom_domain_query_status */
    u32 resolution;     /* dom_domain_resolution */
    u32 confidence;     /* dom_domain_confidence */
    u32 refusal_reason; /* dom_domain_refusal_reason */
    u32 cost_units;
    u32 budget_used;
    u32 budget_max;
} dom_domain_query_meta;

typedef struct dom_domain_distance_result {
    q16_16 distance;
    dom_domain_query_meta meta;
} dom_domain_distance_result;

typedef struct dom_domain_closest_point_result {
    dom_domain_point point;
    q16_16 distance;
    dom_domain_query_meta meta;
} dom_domain_closest_point_result;

typedef struct dom_domain_ray {
    dom_domain_point origin;
    dom_domain_point direction;
    q16_16 max_distance;
} dom_domain_ray;

typedef struct dom_domain_ray_hit_result {
    d_bool hit;
    dom_domain_point point;
    q16_16 distance;
    dom_domain_query_meta meta;
} dom_domain_ray_hit_result;

void dom_domain_budget_init(dom_domain_budget* budget, u32 max_units);
d_bool dom_domain_budget_consume(dom_domain_budget* budget, u32 cost_units);

d_bool dom_domain_contains(const dom_domain_volume* volume,
                           const dom_domain_point* point,
                           dom_domain_budget* budget,
                           dom_domain_query_meta* out_meta);

dom_domain_distance_result dom_domain_distance(const dom_domain_volume* volume,
                                               const dom_domain_point* point,
                                               dom_domain_budget* budget);

dom_domain_closest_point_result dom_domain_closest_point(const dom_domain_volume* volume,
                                                         const dom_domain_point* point,
                                                         dom_domain_budget* budget);

dom_domain_ray_hit_result dom_domain_ray_intersect(const dom_domain_volume* volume,
                                                   const dom_domain_ray* ray,
                                                   dom_domain_budget* budget);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_DOMAIN_QUERY_H */
