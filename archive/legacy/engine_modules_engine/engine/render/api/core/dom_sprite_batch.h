/*
FILE: source/domino/render/api/core/dom_sprite_batch.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_sprite_batch
RESPONSIBILITY: Defines internal contract for `dom_sprite_batch`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SPRITE_BATCH_H
#define DOM_SPRITE_BATCH_H

#include "dom_draw_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct DomSpriteBatch {
    DomDrawCommandBuffer buffer;
} DomSpriteBatch;

void dom_sprite_batch_init(DomSpriteBatch *batch);
dom_err_t dom_sprite_batch_push(DomSpriteBatch *batch,
                                const DomDrawCommand *cmd);
const DomDrawCommandBuffer *dom_sprite_batch_commands(const DomSpriteBatch *batch);

#ifdef __cplusplus
}
#endif

#endif /* DOM_SPRITE_BATCH_H */
