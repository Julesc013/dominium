/*
FILE: game/core/life/lineage.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements lineage registry with deterministic ordering.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Lineage ordering must be deterministic.
*/
#include "dominium/life/lineage.h"

#include <string.h>

void life_lineage_registry_init(life_lineage_registry* reg,
                                life_lineage_record* storage,
                                u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->records = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_lineage_record) * (size_t)capacity);
    }
}

const life_lineage_record* life_lineage_find(const life_lineage_registry* reg,
                                             u64 person_id)
{
    u32 i;
    if (!reg || !reg->records) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->records[i].person_id == person_id) {
            return &reg->records[i];
        }
    }
    return 0;
}

int life_lineage_set(life_lineage_registry* reg,
                     const life_lineage_record* record)
{
    u32 i;
    if (!reg || !record || !reg->records) {
        return -1;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->records[i].person_id == record->person_id) {
            reg->records[i] = *record;
            return 0;
        }
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    reg->records[reg->count++] = *record;
    return 0;
}
