/*
FILE: include/domino/dknowledge.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dknowledge
RESPONSIBILITY: Defines the public contract for `dknowledge` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DKNOWLEDGE_H
#define DOMINO_DKNOWLEDGE_H

#include "dnumeric.h"
#include "dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t KnowledgeId;

typedef enum {
    KNOW_TILE_VISIBILITY = 0,
    KNOW_ENTITY_SEEN,
    KNOW_MARKET_INFO,
} KnowledgeType;

typedef struct {
    KnowledgeType type;
    uint32_t      subject_id;    /* tile hash, entity id, market id, etc. */
} KnowledgeKey;

typedef struct {
    KnowledgeKey key;
    SimTick      last_seen_tick;
    Q16_16       confidence_0_1;
} KnowledgeRecord;

typedef struct {
    KnowledgeId     id;
    KnowledgeRecord *records;
    U32              record_count;
    U32              record_capacity;
} KnowledgeBase;

KnowledgeId    dknowledge_create(U32 capacity);
KnowledgeBase *dknowledge_get(KnowledgeId id);
void           dknowledge_destroy(KnowledgeId id);

void dknowledge_observe(KnowledgeId id,
                        const KnowledgeKey *key,
                        SimTick tick,
                        Q16_16 confidence);

const KnowledgeRecord *dknowledge_query(const KnowledgeBase *kb,
                                        const KnowledgeKey *key);

void dknowledge_mark_tile_visible(KnowledgeId id,
                                  TileCoord x,
                                  TileCoord y,
                                  TileHeight z,
                                  SimTick tick);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DKNOWLEDGE_H */
