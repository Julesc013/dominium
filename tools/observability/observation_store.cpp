/*
FILE: tools/observability/observation_store.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements observation store initialization (read-only).
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Store initialization is deterministic.
*/
#include "observation_store.h"

#include <string.h>

void tool_observation_store_init(tool_observation_store* store,
                                 const tool_observation_store_desc* desc)
{
    if (!store) {
        return;
    }
    memset(store, 0, sizeof(*store));
    if (!desc) {
        return;
    }
    *store = *desc;
}
