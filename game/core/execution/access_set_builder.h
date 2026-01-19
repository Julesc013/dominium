/*
FILE: game/core/execution/access_set_builder.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Deterministic AccessSet builder helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Explicit ranges, stable append ordering.
*/
#ifndef DOMINIUM_CORE_EXECUTION_ACCESS_SET_BUILDER_H
#define DOMINIUM_CORE_EXECUTION_ACCESS_SET_BUILDER_H

#include "domino/core/types.h"
#include "domino/execution/access_set.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_access_set_builder {
    dom_access_set*    sets;
    u32                set_count;
    u32                set_capacity;
    dom_access_range*  read_ranges;
    u32                read_count;
    u32                read_capacity;
    dom_access_range*  write_ranges;
    u32                write_count;
    u32                write_capacity;
    dom_access_range*  reduce_ranges;
    u32                reduce_count;
    u32                reduce_capacity;
    dom_access_set*    current;
    u32                current_read_start;
    u32                current_write_start;
    u32                current_reduce_start;
} dom_access_set_builder;

static inline void dom_access_set_builder_init(dom_access_set_builder* builder,
                                               dom_access_set* set_storage,
                                               u32 set_capacity,
                                               dom_access_range* read_storage,
                                               u32 read_capacity,
                                               dom_access_range* write_storage,
                                               u32 write_capacity,
                                               dom_access_range* reduce_storage,
                                               u32 reduce_capacity)
{
    if (!builder) {
        return;
    }
    builder->sets = set_storage;
    builder->set_count = 0u;
    builder->set_capacity = set_capacity;
    builder->read_ranges = read_storage;
    builder->read_count = 0u;
    builder->read_capacity = read_capacity;
    builder->write_ranges = write_storage;
    builder->write_count = 0u;
    builder->write_capacity = write_capacity;
    builder->reduce_ranges = reduce_storage;
    builder->reduce_count = 0u;
    builder->reduce_capacity = reduce_capacity;
    builder->current = (dom_access_set*)0;
    builder->current_read_start = 0u;
    builder->current_write_start = 0u;
    builder->current_reduce_start = 0u;
}

static inline void dom_access_set_builder_reset(dom_access_set_builder* builder)
{
    if (!builder) {
        return;
    }
    builder->set_count = 0u;
    builder->read_count = 0u;
    builder->write_count = 0u;
    builder->reduce_count = 0u;
    builder->current = (dom_access_set*)0;
    builder->current_read_start = 0u;
    builder->current_write_start = 0u;
    builder->current_reduce_start = 0u;
}

static inline dom_access_set* dom_access_set_builder_begin(dom_access_set_builder* builder,
                                                           u64 access_id,
                                                           u32 reduction_op,
                                                           d_bool commutative)
{
    if (!builder || !builder->sets) {
        return (dom_access_set*)0;
    }
    if (builder->current) {
        return (dom_access_set*)0;
    }
    if (builder->set_count >= builder->set_capacity) {
        return (dom_access_set*)0;
    }
    builder->current = &builder->sets[builder->set_count++];
    builder->current->access_id = access_id;
    builder->current->read_ranges = (const dom_access_range*)0;
    builder->current->read_count = 0u;
    builder->current->write_ranges = (const dom_access_range*)0;
    builder->current->write_count = 0u;
    builder->current->reduce_ranges = (const dom_access_range*)0;
    builder->current->reduce_count = 0u;
    builder->current->reduction_op = reduction_op;
    builder->current->commutative = commutative;
    builder->current_read_start = builder->read_count;
    builder->current_write_start = builder->write_count;
    builder->current_reduce_start = builder->reduce_count;
    return builder->current;
}

static inline int dom_access_set_builder_add_read(dom_access_set_builder* builder,
                                                  const dom_access_range* range)
{
    if (!builder || !range || !builder->current) {
        return -1;
    }
    if (!builder->read_ranges || builder->read_capacity == 0u) {
        return -2;
    }
    if (builder->read_count >= builder->read_capacity) {
        return -3;
    }
    builder->read_ranges[builder->read_count++] = *range;
    return 0;
}

static inline int dom_access_set_builder_add_write(dom_access_set_builder* builder,
                                                   const dom_access_range* range)
{
    if (!builder || !range || !builder->current) {
        return -1;
    }
    if (!builder->write_ranges || builder->write_capacity == 0u) {
        return -2;
    }
    if (builder->write_count >= builder->write_capacity) {
        return -3;
    }
    builder->write_ranges[builder->write_count++] = *range;
    return 0;
}

static inline int dom_access_set_builder_add_reduce(dom_access_set_builder* builder,
                                                    const dom_access_range* range)
{
    if (!builder || !range || !builder->current) {
        return -1;
    }
    if (!builder->reduce_ranges || builder->reduce_capacity == 0u) {
        return -2;
    }
    if (builder->reduce_count >= builder->reduce_capacity) {
        return -3;
    }
    builder->reduce_ranges[builder->reduce_count++] = *range;
    return 0;
}

static inline int dom_access_set_builder_finalize(dom_access_set_builder* builder)
{
    if (!builder || !builder->current) {
        return -1;
    }
    if (builder->read_count > builder->current_read_start) {
        builder->current->read_ranges = builder->read_ranges + builder->current_read_start;
        builder->current->read_count = builder->read_count - builder->current_read_start;
    }
    if (builder->write_count > builder->current_write_start) {
        builder->current->write_ranges = builder->write_ranges + builder->current_write_start;
        builder->current->write_count = builder->write_count - builder->current_write_start;
    }
    if (builder->reduce_count > builder->current_reduce_start) {
        builder->current->reduce_ranges = builder->reduce_ranges + builder->current_reduce_start;
        builder->current->reduce_count = builder->reduce_count - builder->current_reduce_start;
    }
    builder->current = (dom_access_set*)0;
    builder->current_read_start = 0u;
    builder->current_write_start = 0u;
    builder->current_reduce_start = 0u;
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_EXECUTION_ACCESS_SET_BUILDER_H */
