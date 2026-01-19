/*
FILE: include/dominium/execution/work_ir_emit.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Bounded Work IR emission helpers (game-side).
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
*/
#ifndef DOMINIUM_WORK_IR_EMIT_H
#define DOMINIUM_WORK_IR_EMIT_H

#include "domino/core/types.h"
#include "domino/execution/work_ir.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_work_ir_emitter {
    const dom_work_item **items;
    u32                  count;
    u32                  capacity;
} dom_work_ir_emitter;

void dom_work_ir_emitter_init(dom_work_ir_emitter *emit,
                              const dom_work_item **storage,
                              u32 capacity);

int dom_work_ir_emit(dom_work_ir_emitter *emit, const dom_work_item *item);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_WORK_IR_EMIT_H */
