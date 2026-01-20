/*
Kernel interface tests (KERN0).
*/
#include "domino/execution/kernel_iface.h"
#include "execution/kernels/kernel_registry.h"
#include "domino/execution/task_node.h"

#include <stdio.h>
#include <string.h>
#include <new>
#include <stdlib.h>

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static unsigned int g_last_backend = 0u;
static unsigned int g_alloc_count = 0u;

void* operator new(size_t size) throw(std::bad_alloc)
{
    void* ptr = malloc(size);
    if (!ptr) {
        throw std::bad_alloc();
    }
    g_alloc_count += 1u;
    return ptr;
}

void* operator new[](size_t size) throw(std::bad_alloc)
{
    void* ptr = malloc(size);
    if (!ptr) {
        throw std::bad_alloc();
    }
    g_alloc_count += 1u;
    return ptr;
}

void operator delete(void* ptr) throw()
{
    free(ptr);
}

void operator delete[](void* ptr) throw()
{
    free(ptr);
}

static void kernel_record(const dom_kernel_call_context& ctx,
                          const dom_component_view*,
                          int,
                          dom_component_view*,
                          int,
                          const void*,
                          size_t,
                          dom_entity_range)
{
    g_last_backend = ctx.backend_id;
}

static int test_registry_determinism(void)
{
    dom_kernel_entry storage_a[4];
    dom_kernel_entry storage_b[4];
    dom_kernel_registry reg_a;
    dom_kernel_registry reg_b;
    dom_kernel_metadata meta;
    dom_kernel_op_id op_id = dom_kernel_op_id_make(101u);
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry_a;
    const dom_kernel_entry* entry_b;

    meta.capability_mask = 0u;
    meta.deterministic = D_TRUE;
    meta.flags = 0u;
    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    dom_kernel_registry_init(&reg_a, storage_a, 4u);
    dom_kernel_registry_init(&reg_b, storage_b, 4u);
    dom_kernel_register(&reg_a, op_id, DOM_KERNEL_BACKEND_SCALAR, kernel_record, &meta);
    dom_kernel_register(&reg_a, op_id, DOM_KERNEL_BACKEND_SIMD, kernel_record, &meta);
    dom_kernel_register(&reg_b, op_id, DOM_KERNEL_BACKEND_SIMD, kernel_record, &meta);
    dom_kernel_register(&reg_b, op_id, DOM_KERNEL_BACKEND_SCALAR, kernel_record, &meta);

    entry_a = dom_kernel_resolve(&reg_a, op_id, &reqs, DOM_DET_STRICT);
    entry_b = dom_kernel_resolve(&reg_b, op_id, &reqs, DOM_DET_STRICT);
    TEST_CHECK(entry_a != 0);
    TEST_CHECK(entry_b != 0);
    TEST_CHECK(entry_a->backend_id == entry_b->backend_id);
    return 0;
}

static int test_determinism_constraints(void)
{
    dom_kernel_entry storage[4];
    dom_kernel_registry reg;
    dom_kernel_metadata det_meta;
    dom_kernel_metadata nondet_meta;
    dom_kernel_op_id op_id = dom_kernel_op_id_make(202u);
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    det_meta.capability_mask = 0u;
    det_meta.deterministic = D_TRUE;
    det_meta.flags = 0u;
    nondet_meta.capability_mask = 0u;
    nondet_meta.deterministic = D_FALSE;
    nondet_meta.flags = 0u;
    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    dom_kernel_registry_init(&reg, storage, 4u);
    dom_kernel_register(&reg, op_id, DOM_KERNEL_BACKEND_SCALAR, kernel_record, &det_meta);
    dom_kernel_register(&reg, op_id, DOM_KERNEL_BACKEND_SIMD, kernel_record, &nondet_meta);

    entry = dom_kernel_resolve(&reg, op_id, &reqs, DOM_DET_STRICT);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_SCALAR);

    entry = dom_kernel_resolve(&reg, op_id, &reqs, DOM_DET_DERIVED);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_SIMD);
    return 0;
}

static int test_scalar_fallback(void)
{
    dom_kernel_entry storage[2];
    dom_kernel_registry reg;
    dom_kernel_metadata meta;
    dom_kernel_op_id op_id = dom_kernel_op_id_make(303u);
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    meta.capability_mask = 0u;
    meta.deterministic = D_TRUE;
    meta.flags = 0u;
    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    dom_kernel_registry_init(&reg, storage, 2u);
    dom_kernel_register(&reg, op_id, DOM_KERNEL_BACKEND_SCALAR, kernel_record, &meta);

    entry = dom_kernel_resolve(&reg, op_id, &reqs, DOM_DET_STRICT);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_SCALAR);
    return 0;
}

static int test_dispatch_no_allocation(void)
{
    dom_kernel_entry storage[2];
    dom_kernel_registry reg;
    dom_kernel_metadata meta;
    dom_kernel_requirements reqs;
    dom_kernel_call call;
    dom_kernel_call_context ctx;
    unsigned int before;
    dom_entity_range range;

    meta.capability_mask = 0u;
    meta.deterministic = D_TRUE;
    meta.flags = 0u;
    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    dom_kernel_registry_init(&reg, storage, 2u);
    dom_kernel_register(&reg, dom_kernel_op_id_make(404u),
                        DOM_KERNEL_BACKEND_SCALAR, kernel_record, &meta);

    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 0u;

    memset(&call, 0, sizeof(call));
    call.op_id = dom_kernel_op_id_make(404u);
    call.inputs = 0;
    call.input_count = 0;
    call.outputs = 0;
    call.output_count = 0;
    call.range = range;
    call.params = 0;
    call.params_size = 0u;
    call.determinism_class = DOM_DET_STRICT;

    before = g_alloc_count;
    TEST_CHECK(dom_kernel_dispatch(&reg, &call, &reqs, &ctx) == 0);
    TEST_CHECK(g_alloc_count == before);
    TEST_CHECK(g_last_backend == DOM_KERNEL_BACKEND_SCALAR);
    return 0;
}

int main(void)
{
    if (test_registry_determinism() != 0) return 1;
    if (test_determinism_constraints() != 0) return 1;
    if (test_scalar_fallback() != 0) return 1;
    if (test_dispatch_no_allocation() != 0) return 1;
    return 0;
}
