/*
FILE: engine/modules/execution/kernels/scalar/op_ids.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/scalar
RESPONSIBILITY: Stable op_id definitions for scalar kernel library.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Stable identifiers only; never reuse values.
*/
#include "execution/kernels/scalar/op_ids.h"

const dom_kernel_op_id DOM_OP_MEM_COPY_VIEW = { 1ull };
const dom_kernel_op_id DOM_OP_MEM_FILL_VIEW = { 2ull };
const dom_kernel_op_id DOM_OP_REDUCE_SUM_INT = { 3ull };
const dom_kernel_op_id DOM_OP_REDUCE_MIN_INT = { 4ull };
const dom_kernel_op_id DOM_OP_REDUCE_MAX_INT = { 5ull };
const dom_kernel_op_id DOM_OP_APPLY_DELTA_PACKED = { 6ull };
const dom_kernel_op_id DOM_OP_BUILD_VISIBILITY_MASK = { 7ull };
