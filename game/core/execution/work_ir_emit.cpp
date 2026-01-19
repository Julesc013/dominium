/*
FILE: game/core/execution/work_ir_emit.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Bounded Work IR emission helpers (game-side).
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
DETERMINISM: Deterministic append ordering only.
*/
#include "dominium/execution/work_ir_emit.h"

void dom_work_ir_emitter_init(dom_work_ir_emitter *emit,
                              const dom_work_item **storage,
                              u32 capacity)
{
    if (!emit) {
        return;
    }
    emit->items = storage;
    emit->count = 0u;
    emit->capacity = capacity;
}

int dom_work_ir_emit(dom_work_ir_emitter *emit, const dom_work_item *item)
{
    if (!emit || !emit->items || !item) {
        return -1;
    }
    if (emit->count >= emit->capacity) {
        return -2;
    }
    emit->items[emit->count++] = item;
    return 0;
}
