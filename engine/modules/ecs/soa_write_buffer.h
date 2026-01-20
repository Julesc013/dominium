/*
FILE: engine/modules/ecs/soa_write_buffer.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: Deterministic write buffer helpers for SoA backend.
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable append ordering only.
*/
#ifndef DOMINO_ECS_SOA_WRITE_BUFFER_H
#define DOMINO_ECS_SOA_WRITE_BUFFER_H

#include "domino/ecs/ecs_storage_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_soa_write_buffer {
    dom_ecs_write_op* ops;
    u32               count;
    u32               capacity;
} dom_soa_write_buffer;

static inline void dom_soa_write_buffer_init(dom_soa_write_buffer* buffer,
                                             dom_ecs_write_op* storage,
                                             u32 capacity)
{
    if (!buffer) {
        return;
    }
    buffer->ops = storage;
    buffer->count = 0u;
    buffer->capacity = capacity;
}

static inline void dom_soa_write_buffer_clear(dom_soa_write_buffer* buffer)
{
    if (!buffer) {
        return;
    }
    buffer->count = 0u;
}

static inline int dom_soa_write_buffer_push(dom_soa_write_buffer* buffer,
                                            const dom_ecs_write_op* op)
{
    if (!buffer || !op || !buffer->ops) {
        return -1;
    }
    if (buffer->count >= buffer->capacity) {
        return -2;
    }
    buffer->ops[buffer->count++] = *op;
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_SOA_WRITE_BUFFER_H */
