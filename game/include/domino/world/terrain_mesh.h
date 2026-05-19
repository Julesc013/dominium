/*
FILE: include/domino/world/terrain_mesh.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/terrain_mesh
RESPONSIBILITY: Deterministic terrain mesh extraction (presentation only).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and sampling.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by TERRAIN0/TERRAIN1 specs.
*/
#ifndef DOMINO_WORLD_TERRAIN_MESH_H
#define DOMINO_WORLD_TERRAIN_MESH_H

#include "domino/world/terrain_surface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_terrain_mesh_stats {
    u64 triangle_count;
    u64 vertex_count;
    u64 hash;
} dom_terrain_mesh_stats;

int dom_terrain_mesh_hash(const dom_terrain_surface* surface,
                          const dom_domain_aabb* bounds,
                          u32 sample_dim,
                          dom_terrain_mesh_stats* out_stats);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_TERRAIN_MESH_H */
