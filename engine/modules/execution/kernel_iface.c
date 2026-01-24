/*
FILE: source/domino/execution/kernel_iface.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / execution/kernel_iface
RESPONSIBILITY: Implements kernel operation identifier helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism must be enforced by callers based on task class.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/execution/kernel_iface.h"

dom_kernel_op_id dom_kernel_op_id_make(u64 value)
{
    dom_kernel_op_id id;
    dom_kernel_op_id *ptr = &id;
    ptr->value = value;
    return id;
}

d_bool dom_kernel_op_id_is_valid(dom_kernel_op_id id)
{
    const dom_kernel_op_id *ptr = &id;
    return (ptr->value != 0u) ? D_TRUE : D_FALSE;
}

d_bool dom_kernel_op_id_equal(dom_kernel_op_id a, dom_kernel_op_id b)
{
    const dom_kernel_op_id *pa = &a;
    const dom_kernel_op_id *pb = &b;
    return (pa->value == pb->value) ? D_TRUE : D_FALSE;
}
