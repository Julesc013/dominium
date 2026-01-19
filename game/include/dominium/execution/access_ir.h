/*
FILE: include/dominium/execution/access_ir.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Access IR declarations for deterministic resource access.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
*/
#ifndef DOMINIUM_ACCESS_IR_H
#define DOMINIUM_ACCESS_IR_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_access_mode {
    DOM_ACCESS_READ = 1,
    DOM_ACCESS_WRITE = 2,
    DOM_ACCESS_READWRITE = 3
} dom_access_mode;

typedef struct dom_access_decl {
    u64            resource_id;
    dom_access_mode mode;
} dom_access_decl;

typedef struct dom_access_set {
    dom_access_decl *items;
    u32              count;
    u32              capacity;
} dom_access_set;

void dom_access_set_init(dom_access_set *set, dom_access_decl *storage, u32 capacity);
void dom_access_set_clear(dom_access_set *set);
int dom_access_set_add(dom_access_set *set, u64 resource_id, dom_access_mode mode);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_ACCESS_IR_H */
