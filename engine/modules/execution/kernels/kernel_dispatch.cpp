/*
FILE: engine/modules/execution/kernels/kernel_dispatch.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Deterministic kernel dispatch entrypoint.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Dispatch selection is stable and deterministic.
*/
#include "execution/kernels/kernel_registry.h"

int dom_kernel_dispatch(const dom_kernel_registry* registry,
                        const dom_kernel_call* call,
                        const dom_kernel_requirements* reqs,
                        dom_kernel_call_context* out_ctx)
{
    const dom_kernel_entry* entry;
    if (!registry || !call || !out_ctx) {
        return -1;
    }
    if (call->input_count < 0 || call->output_count < 0) {
        return -2;
    }
    entry = dom_kernel_resolve(registry, call->op_id, reqs, call->determinism_class);
    if (!entry || !entry->fn) {
        return -3;
    }
    out_ctx->determinism_class = call->determinism_class;
    out_ctx->backend_id = entry->backend_id;
    out_ctx->flags = 0u;
    out_ctx->reserved = 0u;
    entry->fn(*out_ctx,
              call->inputs,
              call->input_count,
              call->outputs,
              call->output_count,
              call->params,
              call->params_size,
              call->range);
    return 0;
}
