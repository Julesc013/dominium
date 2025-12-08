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
