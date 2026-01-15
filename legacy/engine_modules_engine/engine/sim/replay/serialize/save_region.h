/*
FILE: source/domino/sim/replay/serialize/save_region.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/serialize/save_region
RESPONSIBILITY: Defines internal contract for `save_region`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SAVE_REGION_H
#define DOM_SAVE_REGION_H

#include "core_types.h"
#include "world_addr.h"
#include "world_chunk.h"
#include "save_tlv.h"
#include <stdio.h>

#define REGION_MAGIC 0x5245474E /* 'REGN' */

#define CHUNK_SEC_TERRAIN_OVERRIDES   1
#define CHUNK_SEC_OBJECTS             2
#define CHUNK_SEC_EDIT_OPS            3
#define CHUNK_SEC_LOCAL_VOLUMES       4
#define CHUNK_SEC_LOCAL_ENV_STATE     5
#define CHUNK_SEC_LOCAL_NET_STATE     6

typedef struct ChunkEntry {
    ChunkKey3D key;
    u32        offset;
    u32        length;
} ChunkEntry;

typedef struct RegionHeader {
    u32 magic;
    u16 version;
    u16 chunk_count;
} RegionHeader;

b32 save_region_file(const char *path, ChunkRuntime **chunks, u32 chunk_count);
b32 load_region_index(const char *path, RegionHeader *out_header, ChunkEntry **out_entries);

#endif /* DOM_SAVE_REGION_H */
