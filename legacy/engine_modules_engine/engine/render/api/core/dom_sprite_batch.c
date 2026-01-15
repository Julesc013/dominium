/*
FILE: source/domino/render/api/core/dom_sprite_batch.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_sprite_batch
RESPONSIBILITY: Implements `dom_sprite_batch`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_sprite_batch.h"

void dom_sprite_batch_init(DomSpriteBatch *batch)
{
    if (!batch) {
        return;
    }
    dom_draw_cmd_buffer_init(&batch->buffer);
}

dom_err_t dom_sprite_batch_push(DomSpriteBatch *batch,
                                const DomDrawCommand *cmd)
{
    if (!batch) {
        return DOM_ERR_INVALID_ARG;
    }
    return dom_draw_cmd_buffer_push(&batch->buffer, cmd);
}

const DomDrawCommandBuffer *dom_sprite_batch_commands(const DomSpriteBatch *batch)
{
    if (!batch) {
        return 0;
    }
    return &batch->buffer;
}
