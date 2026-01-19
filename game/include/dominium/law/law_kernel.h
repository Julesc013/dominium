/*
FILE: include/dominium/law/law_kernel.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / law
RESPONSIBILITY: Defines the Law Kernel entry points for commands and epistemic gating.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
*/
#ifndef DOMINIUM_LAW_KERNEL_H
#define DOMINIUM_LAW_KERNEL_H

#include <stddef.h>
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_law_result {
    DOM_LAW_ALLOW = 0,
    DOM_LAW_REFUSE = 1,
    DOM_LAW_DEFER = 2
} dom_law_result;

typedef struct dom_law_context {
    u64 authority_id;
    u32 authority_kind;
    u32 reserved;
} dom_law_context;

typedef struct dom_law_intent {
    const char *name;
    const void *payload;
    size_t      payload_size;
} dom_law_intent;

dom_law_result dom_law_check_command(const dom_law_context *ctx, const dom_law_intent *intent);
dom_law_result dom_law_check_query(const dom_law_context *ctx, const dom_law_intent *intent);
dom_law_result dom_law_check_epistemic(const dom_law_context *ctx,
                                       u32 capability_id,
                                       u32 subject_kind,
                                       u64 subject_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LAW_KERNEL_H */
