/*
FILE: engine/modules/execution/kernels/scalar/op_ids.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/scalar
RESPONSIBILITY: Stable op_id definitions for scalar kernel library.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Stable identifiers only; never reuse values.
*/
#ifndef DOMINO_EXECUTION_KERNEL_OP_IDS_H
#define DOMINO_EXECUTION_KERNEL_OP_IDS_H

#include "domino/execution/kernel_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

extern const dom_kernel_op_id DOM_OP_MEM_COPY_VIEW;
extern const dom_kernel_op_id DOM_OP_MEM_FILL_VIEW;
extern const dom_kernel_op_id DOM_OP_REDUCE_SUM_INT;
extern const dom_kernel_op_id DOM_OP_REDUCE_MIN_INT;
extern const dom_kernel_op_id DOM_OP_REDUCE_MAX_INT;
extern const dom_kernel_op_id DOM_OP_APPLY_DELTA_PACKED;
extern const dom_kernel_op_id DOM_OP_BUILD_VISIBILITY_MASK;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_KERNEL_OP_IDS_H */
