/*
FILE: game/core/law/law_kernel.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / law
RESPONSIBILITY: Law Kernel stubs for command/query/epistemic gating.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
DETERMINISM: Pure, side-effect free checks.
*/
#include "dominium/law/law_kernel.h"

dom_law_result dom_law_check_command(const dom_law_context *ctx, const dom_law_intent *intent)
{
    (void)ctx;
    if (!intent || !intent->name) {
        return DOM_LAW_REFUSE;
    }
    return DOM_LAW_ALLOW;
}

dom_law_result dom_law_check_query(const dom_law_context *ctx, const dom_law_intent *intent)
{
    (void)ctx;
    if (!intent || !intent->name) {
        return DOM_LAW_REFUSE;
    }
    return DOM_LAW_ALLOW;
}

dom_law_result dom_law_check_epistemic(const dom_law_context *ctx,
                                       u32 capability_id,
                                       u32 subject_kind,
                                       u64 subject_id)
{
    (void)ctx;
    (void)subject_kind;
    (void)subject_id;
    if (capability_id == 0u) {
        return DOM_LAW_REFUSE;
    }
    return DOM_LAW_ALLOW;
}
