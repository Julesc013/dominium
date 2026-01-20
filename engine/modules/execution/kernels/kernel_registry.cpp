/*
FILE: engine/modules/execution/kernels/kernel_registry.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Deterministic kernel registry implementation.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Resolution must not depend on insertion order.
*/
#include "execution/kernels/kernel_registry.h"
#include "domino/execution/task_node.h"

static u32 dom_kernel_backend_rank(u32 backend_id)
{
    switch (backend_id) {
    case DOM_KERNEL_BACKEND_GPU:
        return 3u;
    case DOM_KERNEL_BACKEND_SIMD:
        return 2u;
    case DOM_KERNEL_BACKEND_SCALAR:
        return 1u;
    default:
        return 0u;
    }
}

static d_bool dom_kernel_requires_determinism(u32 determinism_class)
{
    return (determinism_class != DOM_DET_DERIVED) ? D_TRUE : D_FALSE;
}

void dom_kernel_registry_init(dom_kernel_registry* registry,
                              dom_kernel_entry* storage,
                              u32 capacity)
{
    if (!registry) {
        return;
    }
    registry->entries = storage;
    registry->count = 0u;
    registry->capacity = capacity;
    registry->backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
}

void dom_kernel_registry_set_backend_mask(dom_kernel_registry* registry,
                                          u32 backend_mask)
{
    if (!registry) {
        return;
    }
    registry->backend_mask = backend_mask;
}

int dom_kernel_register(dom_kernel_registry* registry,
                        dom_kernel_op_id op_id,
                        u32 backend_id,
                        dom_kernel_fn fn,
                        const dom_kernel_metadata* meta)
{
    u32 i;
    dom_kernel_entry* entry;
    if (!registry || !registry->entries || registry->capacity == 0u) {
        return -1;
    }
    if (!fn || !dom_kernel_op_id_is_valid(op_id)) {
        return -2;
    }
    if (backend_id >= 32u) {
        return -3;
    }
    if (registry->count >= registry->capacity) {
        return -4;
    }
    for (i = 0u; i < registry->count; ++i) {
        if (dom_kernel_op_id_equal(registry->entries[i].op_id, op_id) &&
            registry->entries[i].backend_id == backend_id) {
            return -5;
        }
    }
    entry = &registry->entries[registry->count++];
    entry->op_id = op_id;
    entry->backend_id = backend_id;
    entry->capability_mask = meta ? meta->capability_mask : 0u;
    entry->deterministic = meta ? meta->deterministic : D_TRUE;
    entry->flags = meta ? meta->flags : 0u;
    entry->fn = fn;
    return 0;
}

const dom_kernel_entry* dom_kernel_resolve(const dom_kernel_registry* registry,
                                           dom_kernel_op_id op_id,
                                           const dom_kernel_requirements* reqs,
                                           u32 determinism_class)
{
    u32 i;
    u32 backend_mask;
    u32 required_caps;
    d_bool require_det;
    const dom_kernel_entry* best = 0;
    u32 best_rank = 0u;

    if (!registry || !registry->entries || registry->count == 0u) {
        return 0;
    }
    if (!dom_kernel_op_id_is_valid(op_id)) {
        return 0;
    }

    backend_mask = registry->backend_mask;
    if (reqs && reqs->backend_mask != 0u) {
        backend_mask &= reqs->backend_mask;
    }
    required_caps = reqs ? reqs->required_capabilities : 0u;
    require_det = dom_kernel_requires_determinism(determinism_class);

    for (i = 0u; i < registry->count; ++i) {
        const dom_kernel_entry* entry = &registry->entries[i];
        u32 rank;
        if (!dom_kernel_op_id_equal(entry->op_id, op_id)) {
            continue;
        }
        if ((backend_mask & (1u << entry->backend_id)) == 0u) {
            continue;
        }
        if ((entry->capability_mask & required_caps) != required_caps) {
            continue;
        }
        if (require_det && !entry->deterministic) {
            continue;
        }
        if ((entry->flags & DOM_KERNEL_META_DERIVED_ONLY) != 0u &&
            determinism_class != DOM_DET_DERIVED) {
            continue;
        }
        rank = dom_kernel_backend_rank(entry->backend_id);
        if (!best || rank > best_rank ||
            (rank == best_rank && entry->backend_id < best->backend_id)) {
            best = entry;
            best_rank = rank;
        }
    }
    return best;
}
