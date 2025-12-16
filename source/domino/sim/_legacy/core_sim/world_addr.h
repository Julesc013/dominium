/*
FILE: source/domino/sim/_legacy/core_sim/world_addr.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/world_addr
RESPONSIBILITY: Defines internal contract for `world_addr`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_WORLD_ADDR_H
#define DOM_WORLD_ADDR_H

#include "core_types.h"
#include "core_fixed.h"

/* Legacy coordinate helpers; new systems should prefer domino/dworld.h. */

#define SEGMENT_LENGTH_METERS   65536
#define SEGMENT_LENGTH_SHIFT    16
#define CHUNK_SIZE_METERS       16
#define CHUNKS_PER_SEGMENT      4096
#define WORLD_Z_MIN_METERS     (-2048)
#define WORLD_Z_MAX_METERS      2048
#define CHUNK_COUNT_Z           256

typedef u8 SegmentIndex;

typedef struct SimPos {
    SegmentIndex sx;
    SegmentIndex sy;
    fix32 x;
    fix32 y;
    fix32 z;
} SimPos;

typedef struct ChunkKey3D {
    i32 gx;
    i32 gy;
    i32 gz;
} ChunkKey3D;

typedef struct SaveLocalPos {
    u16   chunk_x;
    u16   chunk_y;
    u16   chunk_z;
    fix16 lx;
    fix16 ly;
    fix16 lz;
} SaveLocalPos;

void simpos_normalise(SimPos *pos);
void simpos_move(SimPos *pos, fix32 dx, fix32 dy, fix32 dz);

i32  world_local_meter_x(const SimPos *pos);
i32  world_local_meter_y(const SimPos *pos);

void world_chunk_from_simpos(const SimPos *pos, ChunkKey3D *out_key, SaveLocalPos *out_local);
void world_simpos_from_chunk(const ChunkKey3D *key, const SaveLocalPos *local, SimPos *out_pos);

#endif /* DOM_WORLD_ADDR_H */
