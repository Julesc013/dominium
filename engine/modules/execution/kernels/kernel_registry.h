/*
FILE: engine/modules/execution/kernels/kernel_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Deterministic kernel registry and dispatch helpers.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Resolution must not depend on insertion order.
*/
#ifndef DOMINO_EXECUTION_KERNEL_REGISTRY_H
#define DOMINO_EXECUTION_KERNEL_REGISTRY_H

#include "domino/core/types.h"
#include "domino/execution/kernel_iface.h"
#include "execution/kernels/kernel_params.h"

#ifdef __cplusplus

typedef struct dom_kernel_metadata {
    u32   capability_mask;
    d_bool deterministic;
    u32   flags;
} dom_kernel_metadata;

enum {
    DOM_KERNEL_META_DERIVED_ONLY = 1u << 0
};

typedef struct dom_kernel_entry {
    dom_kernel_op_id op_id;
    u32              backend_id;
    u32              capability_mask;
    d_bool           deterministic;
    u32              flags;
    dom_kernel_fn    fn;
} dom_kernel_entry;

typedef struct dom_kernel_registry {
    dom_kernel_entry* entries;
    u32               count;
    u32               capacity;
    u32               backend_mask;
} dom_kernel_registry;

void dom_kernel_registry_init(dom_kernel_registry* registry,
                              dom_kernel_entry* storage,
                              u32 capacity);
void dom_kernel_registry_set_backend_mask(dom_kernel_registry* registry,
                                          u32 backend_mask);
int dom_kernel_register(dom_kernel_registry* registry,
                        dom_kernel_op_id op_id,
                        u32 backend_id,
                        dom_kernel_fn fn,
                        const dom_kernel_metadata* meta);
const dom_kernel_entry* dom_kernel_resolve(const dom_kernel_registry* registry,
                                           dom_kernel_op_id op_id,
                                           const dom_kernel_requirements* reqs,
                                           u32 determinism_class);
int dom_kernel_dispatch(const dom_kernel_registry* registry,
                        const dom_kernel_call* call,
                        const dom_kernel_requirements* reqs,
                        dom_kernel_call_context* out_ctx);

#endif /* __cplusplus */

#endif /* DOMINO_EXECUTION_KERNEL_REGISTRY_H */
