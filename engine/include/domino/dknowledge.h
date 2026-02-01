/*
FILE: include/domino/dknowledge.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dknowledge
RESPONSIBILITY: Defines the public contract for `dknowledge` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DKNOWLEDGE_H
#define DOMINO_DKNOWLEDGE_H

#include "dnumeric.h"
#include "dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

/* KnowledgeId: Identifier type for Knowledge objects in `dknowledge`. */
typedef uint32_t KnowledgeId;

/* KnowledgeType: Public type used by `dknowledge`. */
typedef enum {
    KNOW_TILE_VISIBILITY = 0,
    KNOW_ENTITY_SEEN,
    KNOW_MARKET_INFO,
} KnowledgeType;

/* KnowledgeKey: Public type used by `dknowledge`. */
typedef struct {
    KnowledgeType type;
    uint32_t      subject_id;    /* tile hash, entity id, market id, etc. */
} KnowledgeKey;

/* KnowledgeRecord: Public type used by `dknowledge`. */
typedef struct {
    KnowledgeKey key;
    SimTick      last_seen_tick;
    Q16_16       confidence_0_1;
} KnowledgeRecord;

/* KnowledgeBase: Public type used by `dknowledge`. */
typedef struct {
    KnowledgeId     id;
    KnowledgeRecord *records;
    U32              record_count;
    U32              record_capacity;
} KnowledgeBase;

/* Purpose: Create dknowledge.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
KnowledgeId    dknowledge_create(U32 capacity);
/* Purpose: Get dknowledge.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
KnowledgeBase *dknowledge_get(KnowledgeId id);
/* Purpose: Destroy dknowledge.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           dknowledge_destroy(KnowledgeId id);

/* Purpose: Observe dknowledge.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dknowledge_observe(KnowledgeId id,
                        const KnowledgeKey *key,
                        SimTick tick,
                        Q16_16 confidence);

/* Purpose: Query dknowledge.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const KnowledgeRecord *dknowledge_query(const KnowledgeBase *kb,
                                        const KnowledgeKey *key);

/* Purpose: Mark tile visible.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dknowledge_mark_tile_visible(KnowledgeId id,
                                  TileCoord x,
                                  TileCoord y,
                                  TileHeight z,
                                  SimTick tick);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DKNOWLEDGE_H */
