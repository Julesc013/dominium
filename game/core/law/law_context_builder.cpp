/*
FILE: game/core/law/law_context_builder.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / law
RESPONSIBILITY: Build law contexts from jurisdiction resolution results.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
DETERMINISM: Pure mapping; no side effects.
*/
#include "game/core/law/jurisdiction_resolver.h"

#include <string.h>

void dom_law_context_build(dom_law_context* ctx,
                           u64 authority_id,
                           u32 authority_kind,
                           const dom_jurisdiction_resolution* res)
{
    u32 i;
    if (!ctx) {
        return;
    }
    memset(ctx, 0, sizeof(*ctx));
    ctx->authority_id = authority_id;
    ctx->authority_kind = authority_kind;

    if (!res) {
        return;
    }
    ctx->jurisdiction_count = res->ordered.count;
    if (ctx->jurisdiction_count > DOM_LAW_MAX_JURISDICTIONS) {
        ctx->jurisdiction_count = DOM_LAW_MAX_JURISDICTIONS;
    }
    for (i = 0u; i < ctx->jurisdiction_count; ++i) {
        ctx->jurisdiction_ids[i] = res->ordered.ids[i];
    }
    ctx->jurisdiction_flags = 0u;
    if (res->refused) {
        ctx->jurisdiction_flags |= 1u;
    }
    if (res->uncertain) {
        ctx->jurisdiction_flags |= 2u;
    }
}
