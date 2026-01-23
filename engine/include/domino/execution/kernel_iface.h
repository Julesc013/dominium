/*
FILE: include/domino/execution/kernel_iface.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/kernel_iface
RESPONSIBILITY: Defines the kernel dispatch interface for compute backends.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism must be enforced by callers based on task class.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_EXECUTION_KERNEL_IFACE_H
#define DOMINO_EXECUTION_KERNEL_IFACE_H

#include "domino/ecs/ecs_component_view.h"
#include "domino/ecs/ecs_entity_range.h"

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_kernel_op_id {
    u64 value;
} dom_kernel_op_id;

static dom_kernel_op_id dom_kernel_op_id_make(u64 value)
{
    dom_kernel_op_id id;
    dom_kernel_op_id *ptr = &id;
    ptr->value = value;
    return id;
}

static d_bool dom_kernel_op_id_is_valid(dom_kernel_op_id id)
{
    const dom_kernel_op_id *ptr = &id;
    return (ptr->value != 0u) ? D_TRUE : D_FALSE;
}

static d_bool dom_kernel_op_id_equal(dom_kernel_op_id a, dom_kernel_op_id b)
{
    const dom_kernel_op_id *pa = &a;
    const dom_kernel_op_id *pb = &b;
    return (pa->value == pb->value) ? D_TRUE : D_FALSE;
}

typedef enum dom_kernel_backend_id {
    DOM_KERNEL_BACKEND_SCALAR = 0u,
    DOM_KERNEL_BACKEND_SIMD   = 1u,
    DOM_KERNEL_BACKEND_GPU    = 2u
} dom_kernel_backend_id;

#define DOM_KERNEL_BACKEND_MASK_SCALAR (1u << DOM_KERNEL_BACKEND_SCALAR)
#define DOM_KERNEL_BACKEND_MASK_SIMD   (1u << DOM_KERNEL_BACKEND_SIMD)
#define DOM_KERNEL_BACKEND_MASK_GPU    (1u << DOM_KERNEL_BACKEND_GPU)
#define DOM_KERNEL_BACKEND_MASK_ALL    (DOM_KERNEL_BACKEND_MASK_SCALAR | \
                                        DOM_KERNEL_BACKEND_MASK_SIMD | \
                                        DOM_KERNEL_BACKEND_MASK_GPU)

typedef struct dom_kernel_call_context {
    u32 determinism_class;
    u32 backend_id;
    u32 flags;
    u32 reserved;
} dom_kernel_call_context;

typedef struct dom_kernel_call {
    dom_kernel_op_id       op_id;
    const dom_component_view* inputs;
    int                   input_count;
    dom_component_view*    outputs;
    int                   output_count;
    dom_entity_range       range;
    const void*            params;
    size_t                 params_size;
    u32                    determinism_class;
} dom_kernel_call;

#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus

typedef void (*dom_kernel_fn)(
    const dom_kernel_call_context& ctx,
    const dom_component_view* inputs, int input_count,
    dom_component_view* outputs, int output_count,
    const void* params, size_t params_size,
    dom_entity_range range
);

#endif /* __cplusplus */

#endif /* DOMINO_EXECUTION_KERNEL_IFACE_H */
