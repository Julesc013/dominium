/*
FILE: source/domino/execution/execution_context.cpp
MODULE: Domino
RESPONSIBILITY: Law evaluation and audit hooks for execution.
*/
#include "domino/execution/execution_context.h"

dom_law_decision dom_execution_context_evaluate_law(const dom_execution_context *ctx,
                                                    const dom_task_node *node) {
    dom_law_decision decision;
    decision.kind = DOM_LAW_ACCEPT;
    decision.refusal_code = 0u;
    decision.transformed_fidelity_tier = 0u;
    decision.transformed_next_due_tick = DOM_EXEC_TICK_INVALID;

    if (!ctx) {
        return decision;
    }
    if (ctx->evaluate_law) {
        return ctx->evaluate_law(ctx, node, ctx->user_data);
    }
    return decision;
}

void dom_execution_context_record_audit(const dom_execution_context *ctx,
                                        const dom_audit_event *event) {
    if (!ctx || !ctx->record_audit) {
        return;
    }
    ctx->record_audit(ctx, event, ctx->user_data);
}

const dom_access_set *dom_execution_context_lookup_access_set(const dom_execution_context *ctx,
                                                              u64 access_set_id) {
    if (!ctx || !ctx->lookup_access_set) {
        return 0;
    }
    return ctx->lookup_access_set(ctx, access_set_id, ctx->user_data);
}
